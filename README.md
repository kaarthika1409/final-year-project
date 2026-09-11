# Personalized Nutritional Prediction and Adaptive Dietary Recommendation System

An end-to-end health & nutrition prediction platform featuring Mifflin-St Jeor BMR calorie budgeting, manual & PyTorch vision photo food logging, real-time adaptive meal slot target redistribution, adaptive recommendation engine, and demographic accuracy evaluation module.

---

## Tech Stack

- **Backend**: Python, FastAPI, SQLAlchemy, Alembic (database migrations), Pydantic, RapidFuzz, PyJWT, Passlib (bcrypt)
- **Database**: PostgreSQL / SQLite (`nutrition_app.db`)
- **AI/ML**: PyTorch, torchvision (EfficientNet-B0 fine-tuning), scikit-learn & numpy evaluation metrics
- **Frontend**: React (Vite web dashboard app), TailwindCSS, Lucide icons, Recharts visualization
- **Auth**: JWT Authentication (access tokens with Bearer authorization)

---

## Folder Structure

```
├── backend/
│   ├── alembic/                  # Alembic database migration scripts
│   │   ├── versions/             # Database schema migration files
│   │   └── env.py
│   ├── app/
│   │   ├── budget_engine.py      # Mifflin-St Jeor formula & BMR/TDEE calculation
│   │   ├── database.py           # SQLAlchemy engine & SessionLocal maker
│   │   ├── evaluation.py         # MAE, RMSE, and MAPE demographic accuracy engine
│   │   ├── main.py               # FastAPI application entrypoint & OpenAPI docs
│   │   ├── ml_service.py         # PyTorch food image classification & portion heuristic
│   │   ├── models.py             # ORM models (User, MealSlot, MealLog, NutritionReference, DailyTarget)
│   │   ├── recommendation.py     # Macro fit ranking & hard allergen filtering engine
│   │   ├── redistribution.py     # Stage 3 Adaptive Calorie Redistribution algorithm & guardrails
│   │   ├── schemas.py            # Pydantic data schemas
│   │   ├── security.py           # Password hashing & JWT token processing
│   │   ├── seed_data.py          # Reference dataset catalog
│   │   └── routers/              # Modular API endpoints
│   │       ├── analytics.py      # /analytics/accuracy & /analytics/deficiencies
│   │       ├── auth.py           # /auth/signup, /auth/login, /auth/me, /calorie-budget/calculate
│   │       ├── meals.py          # /meals/manual, /meals/photo, /meals/search
│   │       ├── recommendations.py# /recommendations
│   │       └── targets.py        # /dashboard/today & /targets/recalculate
│   ├── tests/
│   │   ├── test_api.py           # Full API integration & stage checkpoint tests
│   │   └── test_redistribution.py# Dedicated pytest suite for redistribution algorithm
│   └── requirements.txt          # Backend dependencies
├── ml/
│   ├── train_food_classifier.py  # PyTorch model fine-tuning module
│   └── evaluate_model.py         # Standalone accuracy report module
├── frontend/                     # React (Vite) web dashboard application
│   ├── src/
│   │   ├── components/           # CalorieRing, MealSlotCard, PhotoUploadModal, ManualEntryModal, SuggestionsModal, DemographicAccuracyChart
│   │   ├── pages/                # Login, Signup, Dashboard, Profile, Analytics
│   │   ├── api.js                # Frontend API client
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   └── package.json
├── .env.example                  # Environment configuration template
├── seed_nutrition_data.py        # USDA FoodData Central & catalog seeder
├── train_model.py                # Food image recognition training script
├── evaluate_accuracy.py          # Stage 6 accuracy evaluation, CSV & chart generator
├── requirements.txt              # Root dependency file
└── README.md
```

---

## Stage-by-Stage Implementation Overview

### STAGE 1 — Database Schema, Auth & Calorie Budget Engine
- SQLAlchemy ORM models: `users`, `meal_slots`, `meal_logs`, `nutrition_reference`, `daily_targets`.
- JWT Signup, Login, and Profile endpoints (`/auth/signup`, `/auth/login`, `/auth/me`).
- Mifflin-St Jeor BMR calculator, activity multipliers (TDEE), and goal adjustment.
- Endpoint `POST /calorie-budget/calculate` returning target calories & initial meal slot targets.

### STAGE 2 — Manual Meal Logging & Nutrition Reference Seeding
- Seeder script `seed_nutrition_data.py` populates reference foods from USDA FoodData Central / catalog.
- Endpoint `POST /meals/manual`: fuzzy matches food query using `rapidfuzz`, computes calories/macros based on gram portion, logs entry, and updates daily target progress.
- Endpoint `GET /dashboard/today`: returns consumed, remaining, and target calories.

### STAGE 3 — Adaptive Meal Slot Redistribution Engine
- Algorithm redistributes over/under-eaten calorie delta $\Delta_i$ across remaining unconsumed meal slots.
- Enforces guardrails: `floor_kcal = 300` kcal minimum per slot, `max_variance = 20%` of daily target calories maximum swing above planned.
- Dedicated unit test suite in `backend/tests/test_redistribution.py`.

### STAGE 4 — Food Image Recognition
- Endpoint `POST /meals/photo`: accepts photo upload, runs PyTorch EfficientNet-B0 image classifier, applies portion size heuristic, and returns detected food, calories, macros, and `confidence_score`.
- Flags low-confidence results (`confidence < 0.5`) as `uncertain: true` for user confirmation.
- Training pipeline script `train_model.py` fine-tunes CNN checkpoint and outputs model weights `ml/food_classifier_weights.pth`.

### STAGE 5 — Adaptive Dietary Recommendation Engine
- Endpoint `GET /recommendations`: pulls remaining calories and macros, checks dietary preferences (vegan, vegetarian, keto, balanced), and applies a **hard allergen filter** to strictly exclude any user allergens.
- Ranks candidate foods by calorie and macro fit score.

### STAGE 6 — Demographic Accuracy Evaluation Module
- Script `evaluate_accuracy.py` & endpoint `GET /analytics/accuracy`: evaluates prediction performance across Age bands (<30, 30-50, >50), Gender (Male, Female), and BMI categories (Underweight, Normal, Overweight, Obese).
- Computes **MAE**, **RMSE**, and **MAPE** (Mean Absolute Percentage Error %).
- Generates formatted CSV table `accuracy_results.csv` and bar chart visualization `accuracy_chart.png`.

### STAGE 7 — Nutritional Deficiency Flagging (Optional Engine)
- Endpoint `GET /analytics/deficiencies`: calculates rolling 7-day nutrient intake vs RDA reference standards and flags any nutrient trending below 70% of RDA over the window.

---

## Instructions: How to Run the Project

### 1. Environment Setup

```bash
# Clone or navigate to the project directory
cd "c:\Users\kaart\OneDrive\Desktop\4th year"

# Install backend Python dependencies
python -m pip install -r requirements.txt
```

### 2. Database Migrations (Alembic)

```bash
# Run database schema migrations
python -m alembic upgrade head
```

### 3. Seed Nutrition Database (USDA FoodData Central / Reference Data)

```bash
# Populate reference foods into database
python seed_nutrition_data.py
```

### 4. Train / Fine-Tune Vision Food Recognition Model

```bash
# Train PyTorch food classifier and save model weights
python train_model.py --epochs 2 --batch_size 8
```

### 5. Run Demographic Accuracy Evaluation & Results Export

```bash
# Computes MAE, RMSE, MAPE and generates accuracy_results.csv & accuracy_chart.png
python evaluate_accuracy.py
```

### 6. Run Pytest Test Suite

```bash
# Runs full unit & integration test suite (budget, redistribution, manual log, photo, recommendations)
python -m pytest -v
```

### 7. Start FastAPI Backend Server

```bash
# Start backend on http://localhost:8000
python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```
- Interactive Swagger/OpenAPI Documentation is live at: **[http://localhost:8000/docs](http://localhost:8000/docs)**

### 8. Start React Frontend Web Application

```bash
# Navigate to frontend folder
cd frontend

# Install Node dependencies
npm install

# Start Vite React dev server
npm run dev
```
- Access the web dashboard in browser at: **[http://localhost:5173](http://localhost:5173)**
