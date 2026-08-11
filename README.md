# Personalized Nutritional Prediction and Adaptive Dietary Recommendation System

An AI-powered full-stack health platform providing Mifflin-St Jeor BMR calorie budgeting, manual & PyTorch vision food image logging, real-time adaptive meal slot target redistribution, dietary recommendation engine, and demographic accuracy evaluation.

---

## Key Features

1. **User Authentication & Profile**: JWT signup/login tracking Age, Weight (kg), Height (cm), Gender, Activity Level, Dietary Goal (Lose/Maintain/Gain), Dietary Preferences (Vegan, Vegetarian, Keto, Balanced), and Allergies.
2. **Calorie Budget Engine**: Basal Metabolic Rate (BMR) calculation via Mifflin-St Jeor equation + activity multiplier (TDEE) + goal adjustment (-500 kcal for weight loss, +500 for gain).
3. **Meal Logging API**:
   - **Manual Search & Log**: Search in a 50+ item Nutrition Reference Database with gram weight quantity selector.
   - **AI Photo Upload Recognition**: Pretrained PyTorch CNN (EfficientNet-B0) food classifier + portion heuristic + fuzzy string matching against database nutrition reference table.
4. **Adaptive Redistribution Logic**: Recalculates remaining daily calories after every logged meal and dynamically adjusts upcoming meal slot targets (Breakfast, Lunch, Snacks, Dinner).
5. **Adaptive Recommendation Engine**: Suggests 3-5 safe and optimal food options tailored to remaining calories, macro targets (protein/carbs/fat), user allergies, and dietary preferences.
6. **Demographic Accuracy Evaluation Module**: Evaluates prediction discrepancy across Age (<30, 30-50, >50), Gender (Male, Female), and BMI categories (Underweight, Normal, Overweight, Obese), outputting MAE and RMSE metrics per group.
7. **Modern React Web Dashboard**: Interactive dark-themed UI featuring circular SVG calorie progress ring, 4 adaptive meal slot cards, photo upload modal, manual search modal, AI suggestions drawer, and demographic accuracy charts.

---

## Directory Structure

```
├── backend/
│   ├── app/
│   │   ├── budget_engine.py       # Mifflin-St Jeor formula & BMI logic
│   │   ├── database.py            # SQLAlchemy engine & session maker
│   │   ├── evaluation.py          # Demographic MAE & RMSE evaluation
│   │   ├── main.py                # FastAPI application entrypoint & OpenAPI docs
│   │   ├── ml_service.py          # PyTorch model inference, portion heuristic, fuzzy matching
│   │   ├── models.py              # ORM models (User, MealLog, NutritionReference, DailyTarget)
│   │   ├── recommendation.py      # Macro & allergy filtering meal recommendation engine
│   │   ├── redistribution.py      # Adaptive calorie redistribution logic across meal slots
│   │   ├── schemas.py             # Pydantic request & response schemas
│   │   ├── security.py            # Password hashing (bcrypt) & JWT handling
│   │   ├── seed_data.py           # Populates 50+ nutrition reference database items
│   │   └── routers/
│   │       ├── analytics.py       # Demographic accuracy API route
│   │       ├── auth.py            # Signup, login, profile management routes
│   │       ├── meals.py           # Food search, manual log, photo upload routes
│   │       ├── recommendations.py # Adaptive recommendation route
│   │       └── targets.py         # Daily target & adaptive redistribution routes
│   ├── tests/
│   │   └── test_api.py            # Pytest suite for budget, auth, logging & redistribution
│   └── requirements.txt
├── ml/
│   ├── train_food_classifier.py   # PyTorch fine-tuning script for food classifier
│   └── evaluate_model.py          # Standalone demographic accuracy report generator
├── frontend/
│   ├── src/
│   │   ├── components/            # CalorieRing, MealSlotCard, PhotoUploadModal, ManualEntryModal, SuggestionsModal, DemographicAccuracyChart
│   │   ├── pages/                 # Login, Signup, Dashboard, Profile, Analytics
│   │   ├── api.js                 # API client service layer
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
└── README.md
```

---

## Setup & Running Instructions

### 1. Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### 2. Backend Setup & Run

```bash
# Navigate to project root
cd "c:\Users\kaart\OneDrive\Desktop\4th year"

# Install Python requirements
pip install -r backend/requirements.txt

# Run backend API server with Uvicorn
python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```
- Interactive Swagger OpenAPI documentation is available at: **[http://localhost:8000/docs](http://localhost:8000/docs)**

### 3. Running Backend Test Suite

```bash
python -m pytest backend/tests/test_api.py -v
```

### 4. Running ML Scripts

```bash
# Run demographic accuracy evaluation report (outputs MAE and RMSE per demographic cohort)
python ml/evaluate_model.py

# Run PyTorch food image classifier fine-tuning script
python ml/train_food_classifier.py --epochs 2 --batch_size 16
```

### 5. Frontend Setup & Run

```bash
# Navigate to frontend folder
cd frontend

# Install Node dependencies (if not already installed)
npm install

# Start Vite React development server
npm run dev
```
- Open browser at **[http://localhost:5173](http://localhost:5173)**

---

## OpenAPI Swagger API Documentation

FastAPI auto-generates interactive documentation at `/docs`:
- `POST /api/auth/signup`: Create user profile & calculate Mifflin BMR target.
- `POST /api/auth/login`: Authenticate and receive JWT access token.
- `GET /api/targets/today`: Retrieve today's daily target & adaptive meal slot breakdown.
- `GET /api/meals/search`: Real-time search in 50+ item nutrition database.
- `POST /api/meals/manual`: Log meal manually & recalculate adaptive slot targets.
- `POST /api/meals/photo`: Detect food item & macros from image upload using PyTorch vision model.
- `GET /api/recommendations`: Get top 3-5 meal options matching remaining calories, macros, allergies & preferences.
- `GET /api/analytics/accuracy`: Retrieve demographic MAE & RMSE evaluation report.
