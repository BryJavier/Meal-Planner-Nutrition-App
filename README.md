# 🥗 Meal Planner & Nutrition Tracker

A full-stack web application for planning weekly meals, tracking macronutrients, managing recipes, and getting AI-powered meal suggestions — all in a clean dark-mode interface.

---

## ✨ Features

### 🍽️ Meal Calendar
- Drag-and-drop weekly calendar (Monday–Sunday)
- Four meal slots per day: **Breakfast**, **Lunch**, **Dinner**, **Snack**
- Add any recipe to any slot in one click
- Reorder meals within a slot via drag-and-drop

### 📊 Nutrition Dashboard
- Live macro summary for today: **Calories**, **Protein**, **Carbs**, **Fat**
- Progress bars vs. your personal daily goals
- Calorie split donut chart (protein / carbs / fat kcal breakdown)
- Weekly stacked bar chart with a goal reference line

### 📖 Recipe Manager
- Create, edit, and delete recipes
- Search by name
- Ingredient lookup from a built-in database of 15+ common ingredients
- Auto-calculated nutrition per serving
- Recipe tags (e.g. `high-protein`, `breakfast`)
- Step-by-step instructions

### 🧂 Ingredients Database
- Browse all system and custom ingredients in a sortable table
- Add your own custom ingredients with full macro info
- Edit or delete custom ingredients (system ingredients are read-only)

### 🤖 AI Meal Suggestions (Claude)
- Powered by **Anthropic Claude**
- Suggests 3–5 personalised meals based on your calorie & macro goals and dietary preferences
- One-click AI recipe generation: produces a complete recipe with ingredients and instructions, ready to save

### 👤 User Accounts
- JWT-based authentication with refresh tokens
- Register / log in securely
- Per-user dietary preferences & daily macro goals
- Isolated data per user (recipes, meal plans)

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 18, Vite, Ant Design 5, Recharts, Zustand, dnd-kit, dayjs |
| **Backend** | FastAPI, SQLAlchemy 2 (async), Alembic, Pydantic v2, python-jose, passlib |
| **Database** | PostgreSQL 16 |
| **AI** | Anthropic Claude (`anthropic` SDK) |
| **Infrastructure** | Docker, Docker Compose |

---

## 📋 Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (includes Docker Compose)
- An [Anthropic API key](https://console.anthropic.com/) *(required for AI features)*
- Git

---

## 🚀 Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/meal-planner-nutrition-app.git
cd meal-planner-nutrition-app
```

### 2. Create your environment file

Copy the example and fill in your values:

```bash
cp .env.example .env
```

Open `.env` and set the following variables:

```env
# PostgreSQL
POSTGRES_DB=meal_planner
POSTGRES_USER=mp_user
POSTGRES_PASSWORD=your_secure_password

# JWT
SECRET_KEY=your_random_secret_key        # e.g. run: openssl rand -base64 32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Anthropic (required for AI features)
ANTHROPIC_API_KEY=sk-ant-...
```

> **Tip:** Generate a strong `SECRET_KEY` with:
> ```bash
> openssl rand -base64 32
> ```

### 3. Start the application

```bash
docker compose up --build
```

This will:
1. Start a **PostgreSQL 16** database
2. Run **Alembic migrations** to create all tables
3. **Seed 15 system ingredients** automatically on first boot
4. Start the **FastAPI backend** on `http://localhost:8000`
5. Start the **React frontend** on `http://localhost:5173`

### 4. Open the app

Navigate to **[http://localhost:5173](http://localhost:5173)** and register a new account.

---

## 🗂️ Project Structure

```
.
├── docker-compose.yml
├── .env                        # Your local environment variables (not committed)
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic/                # Database migrations
│   │   └── versions/
│   └── app/
│       ├── main.py             # FastAPI app entry point
│       ├── config.py           # Settings via pydantic-settings
│       ├── database.py         # Async SQLAlchemy engine
│       ├── seed.py             # System ingredient seeding
│       ├── models/             # SQLAlchemy ORM models
│       ├── routers/            # API route handlers
│       ├── schemas/            # Pydantic request/response schemas
│       └── services/           # Business logic (auth, nutrition, AI)
└── frontend/
    ├── Dockerfile
    ├── vite.config.js
    └── src/
        ├── App.jsx             # Routes & theme config
        ├── api/                # Axios API clients
        ├── components/         # Reusable UI components
        │   ├── ai/
        │   ├── calendar/
        │   ├── layout/
        │   ├── nutrition/
        │   └── recipes/
        ├── pages/              # Top-level page components
        ├── store/              # Zustand auth store
        └── hooks/
```

---

## 🔌 API Reference

The backend provides a full REST API documented interactively at:

**[http://localhost:8000/docs](http://localhost:8000/docs)** (Swagger UI)

Key endpoint groups:

| Prefix | Description |
|---|---|
| `POST /api/auth/register` | Create a new user account |
| `POST /api/auth/login` | Obtain access + refresh tokens |
| `GET/POST /api/recipes` | List and create recipes |
| `GET/POST /api/ingredients` | List and create ingredients |
| `GET/POST /api/meal-plans` | Weekly meal plan management |
| `GET /api/nutrition/summary` | Today's macro totals vs goals |
| `GET /api/nutrition/weekly` | Per-day macro breakdown for a week |
| `POST /api/ai/suggestions` | Get AI meal suggestions |
| `POST /api/ai/generate-recipe` | Generate a full recipe with AI |

---

## 🧑‍💻 Development

### Running without Docker (backend only)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Requires a running PostgreSQL instance
export DATABASE_URL=postgresql+asyncpg://mp_user:password@localhost:5434/meal_planner
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### Running without Docker (frontend only)

```bash
cd frontend
npm install
npm run dev
```

### Applying database migrations

```bash
# Inside the backend container
docker compose exec backend alembic upgrade head

# Create a new migration after changing a model
docker compose exec backend alembic revision --autogenerate -m "description"
```

---

## ⚙️ Environment Variables Reference

| Variable | Required | Default | Description |
|---|---|---|---|
| `POSTGRES_DB` | ✅ | — | Database name |
| `POSTGRES_USER` | ✅ | — | Database user |
| `POSTGRES_PASSWORD` | ✅ | — | Database password |
| `SECRET_KEY` | ✅ | — | JWT signing secret (min 32 chars) |
| `ALGORITHM` | ❌ | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | ❌ | `30` | Access token lifetime (minutes) |
| `REFRESH_TOKEN_EXPIRE_DAYS` | ❌ | `7` | Refresh token lifetime (days) |
| `ANTHROPIC_API_KEY` | ✅* | — | Claude API key *(AI features disabled without it)* |

---

## 🐛 Troubleshooting

**Port conflicts**

If port `5173` or `8000` are in use, stop the conflicting process or update the ports in `docker-compose.yml`.

**Database connection errors on first start**

The backend waits for a PostgreSQL healthcheck before starting. If it still fails, run:
```bash
docker compose down -v && docker compose up --build
```

**AI features not working**

Ensure `ANTHROPIC_API_KEY` is set in your `.env` file and the key is valid. The app runs fully without it — only the AI suggestion and recipe generation buttons will be non-functional.

**Ingredients not showing in recipe form**

The seed runs automatically on startup. Check the backend logs to confirm:
```bash
docker compose logs backend | grep -i seed
```

---

## 📄 License

MIT
