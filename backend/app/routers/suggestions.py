from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
from datetime import datetime

from app.database import get_db
from app.models.suggestion import Suggestion
from app.models.recipe import Recipe
from app.models.ingredient import Ingredient
from app.models.recipe_ingredient import RecipeIngredient
from app.dependencies import get_current_user
from app.services.suggestion_service import fetch_meal_suggestion
from app.utils.crypto import decrypt
from pydantic import BaseModel

router = APIRouter(prefix="/api/suggestions", tags=["suggestions"])

class FetchSuggestionRequest(BaseModel):
    meal_slot: str = "lunch"
    preferences: str = None

class SuggestionResponse(BaseModel):
    meal_name: str
    ingredients: list
    prep_time: int
    servings: int
    macros: dict

class ConvertToRecipeRequest(BaseModel):
    meal_name: str
    ingredients: list
    prep_time: int
    servings: int
    macros: dict

@router.post("/fetch", response_model=SuggestionResponse)
async def get_meal_suggestion(
    request: FetchSuggestionRequest,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a new meal suggestion based on meal slot and preferences."""
    try:
        # Get and decrypt user's API key from database
        if not current_user.anthropic_api_key_encrypted:
            raise ValueError("User has not configured an Anthropic API key")
        
        api_key = decrypt(current_user.anthropic_api_key_encrypted)
        suggestion = fetch_meal_suggestion(api_key, request.meal_slot, request.preferences)
        
        # Store suggestion in DB
        db_suggestion = Suggestion(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            meal_name=suggestion["meal_name"],
            ingredients=suggestion["ingredients"],
            prep_time=suggestion["prep_time"],
            servings=suggestion["servings"],
            macros=suggestion["macros"]
        )
        db.add(db_suggestion)
        await db.commit()
        
        return suggestion
    except Exception as e:
        print(f"Error in fetch suggestion: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch suggestion: {str(e)}"
        )

@router.post("/convert-to-recipe")
async def convert_suggestion_to_recipe(
    data: ConvertToRecipeRequest,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Convert a meal suggestion to a saved recipe."""
    try:
        print(f"DEBUG: Converting suggestion to recipe: {data.meal_name}")
        
        # Create recipe with valid fields only
        new_recipe = Recipe(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            name=data.meal_name,
            servings=data.servings,
            prep_time_minutes=data.prep_time,
            is_ai_generated=True,
        )
        db.add(new_recipe)
        
        # Process ingredients - create ingredient entries and link to recipe
        for ing_data in data.ingredients:
            # Create ingredient (AI-generated ingredients stored without macro details)
            ingredient = Ingredient(
                id=str(uuid.uuid4()),
                name=ing_data["name"],
                calories_per_100g=0,
                protein_per_100g=0,
                carbs_per_100g=0,
                fat_per_100g=0,
                unit="g",
                created_by=current_user.id,
            )
            db.add(ingredient)
            
            # Create recipe-ingredient link
            recipe_ingredient = RecipeIngredient(
                id=str(uuid.uuid4()),
                recipe_id=new_recipe.id,
                ingredient_id=ingredient.id,
                quantity_g=ing_data.get("amount", 0),
                display_amount=ing_data.get("amount"),
                display_unit=ing_data.get("unit", "g"),
            )
            db.add(recipe_ingredient)
        
        await db.commit()
        await db.refresh(new_recipe)
        
        print(f"DEBUG: Recipe created successfully: {new_recipe.id}")
        
        return {
            "id": new_recipe.id,
            "name": new_recipe.name,
            "created_at": new_recipe.created_at
        }
    except Exception as e:
        print(f"Error in convert-to-recipe: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create recipe: {str(e)}"
        )
