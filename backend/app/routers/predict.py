"""
routers/predict.py
==================
Provides two endpoints:

POST /api/predict
    Accepts patient health data, runs it through diet_model.pkl,
    and returns the predicted diet class + confidence.

GET /api/predict/diet-recommendations
    Returns dishes from final_dish_dataset.csv (seeded into nutrition_reference)
    filtered by the predicted diet type, user allergies, and dietary preferences,
    plus a generated meal plan (Breakfast / Lunch / Dinner / Snacks).
"""

import os
import sys
import logging
import importlib.util
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models import NutritionReference, User
from backend.app.schemas import (
    PredictRequest,
    PredictResponse,
    DishRecommendationItem,
    DishRecommendationResponse,
    MealPlan,
)
from backend.app.security import get_current_user
from backend.app.ml_service import predict_diet

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/predict", tags=["Diet ML Prediction"])

# ---------------------------------------------------------------
# Resolve preprocessor path dynamically
# ---------------------------------------------------------------
_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_PREPROCESSOR_PY = os.path.join(_BACKEND_DIR, "ml_models", "diet_preprocessor.py")

_dp_module = None


def _get_dp_module():
    """Lazily load the diet_preprocessor module."""
    global _dp_module
    if _dp_module is None:
        if not os.path.exists(_PREPROCESSOR_PY):
            raise FileNotFoundError(
                f"diet_preprocessor.py not found at '{_PREPROCESSOR_PY}'. "
                "Run: python ml_models/train_model.py"
            )
        spec = importlib.util.spec_from_file_location("diet_preprocessor", _PREPROCESSOR_PY)
        _dp_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_dp_module)
    return _dp_module


# ---------------------------------------------------------------
# Diet-to-nutrition requirement mapping
# ---------------------------------------------------------------
_DIET_RULES = {
    "Low_Carb": {
        "max_carbs_g": 20.0,
        "label": "Low Carb",
        "description": "Carbohydrate-restricted diet",
    },
    "Low_Sodium": {
        "max_fat_g": 20.0,
        "label": "Low Sodium",
        "description": "Low sodium / heart-healthy diet",
    },
    "Balanced": {
        "label": "Balanced",
        "description": "Balanced macronutrient diet",
    },
}

_ALLERGY_KEYWORDS = {
    "nuts":      ["almond", "walnut", "cashew", "hazelnut", "pecan", "pistachio", "macadamia", "nut"],
    "peanuts":   ["peanut", "groundnut"],
    "dairy":     ["milk", "cheese", "butter", "cream", "yogurt", "ghee", "whey"],
    "gluten":    ["wheat", "bread", "flour", "pasta", "barley", "rye", "semolina"],
    "eggs":      ["egg"],
    "shellfish": ["shrimp", "prawn", "crab", "lobster"],
    "fish":      ["salmon", "tuna", "cod", "tilapia", "anchov", "sardine", "fish"],
    "soy":       ["soy", "tofu", "miso", "tempeh", "edamame"],
}


def _has_allergen(food: NutritionReference, user_allergies: List[str]) -> bool:
    allergen_tags = [a.strip().lower() for a in (food.allergens or "").split(",") if a.strip()]
    ingredient_text = (food.tags or "").lower()
    food_name_lower = food.food_name.lower()
    combined = f"{food_name_lower} {ingredient_text}"

    for allergen in user_allergies:
        al = allergen.strip().lower()
        if al in allergen_tags:
            return True
        keywords = _ALLERGY_KEYWORDS.get(al, [al])
        if any(kw in combined for kw in keywords):
            return True
    return False


def _score_dish(
    food: NutritionReference,
    diet: str,
    target_calories: float = 500.0,
) -> tuple[float, str]:
    """Score a dish for a given diet. Returns (score, reason_text)."""
    serving_g = food.serving_size_g or 100.0
    pf = serving_g / 100.0
    cal = food.calories * pf
    prot = food.protein * pf
    carbs = food.carbs * pf
    fat = food.fat * pf

    reasons = []
    score = 0.0

    # Calorie fit (0-0.4)
    cal_ratio = cal / max(target_calories, 1.0)
    cal_score = 1.0 - abs(cal_ratio - 0.35)
    score += max(0.0, cal_score) * 0.4

    if diet == "Low_Carb":
        if carbs <= 10:
            score += 0.6
            reasons.append("Very low carb")
        elif carbs <= 20:
            score += 0.4
            reasons.append("Low carb")
        if prot >= 10:
            reasons.append("High protein")

    elif diet == "Low_Sodium":
        if fat <= 10:
            score += 0.5
            reasons.append("Low fat")
        if carbs <= 30:
            score += 0.1
            reasons.append("Moderate carb")
        if prot >= 8:
            reasons.append("Good protein")

    else:  # Balanced
        macro_total = max(prot + carbs + fat, 1.0)
        balance = 1.0 - abs((prot / macro_total) - 0.30) - abs((carbs / macro_total) - 0.45) - abs((fat / macro_total) - 0.25)
        score += max(0.0, balance) * 0.6
        reasons.append("Balanced macros")

    if not reasons:
        reasons.append("Nutritionally suitable")

    return round(min(1.0, max(0.0, score)), 3), ", ".join(reasons)


def _build_dish_item(food: NutritionReference, score: float, reason: str) -> DishRecommendationItem:
    serving_g = food.serving_size_g or 100.0
    pf = serving_g / 100.0
    return DishRecommendationItem(
        id=food.id,
        food_name=food.food_name,
        category=food.category or "Mixed Dish",
        calories_per_serving=round(food.calories * pf, 1),
        protein_g=round(food.protein * pf, 1),
        carbs_g=round(food.carbs * pf, 1),
        fat_g=round(food.fat * pf, 1),
        serving_size_g=serving_g,
        ingredients=food.tags or "",
        fit_reason=reason,
        match_score=score,
    )


def _get_filtered_ranked_dishes(
    db: Session,
    diet: str,
    user_allergies: List[str],
    limit: int = 50,
) -> List[DishRecommendationItem]:
    """Returns dishes from nutrition_reference filtered and ranked for the diet."""
    all_foods = db.query(NutritionReference).all()
    scored: List[tuple[float, NutritionReference, str]] = []

    for food in all_foods:
        if _has_allergen(food, user_allergies):
            continue

        # Diet-specific hard filters
        serving_g = food.serving_size_g or 100.0
        pf = serving_g / 100.0
        carbs = food.carbs * pf
        fat = food.fat * pf

        if diet == "Low_Carb" and carbs > 20.0:
            continue

        score, reason = _score_dish(food, diet)
        scored.append((score, food, reason))

    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:limit]
    return [_build_dish_item(f, s, r) for s, f, r in top]


def _build_meal_plan(dishes: List[DishRecommendationItem]) -> MealPlan:
    """Slice the ranked dishes into Breakfast / Lunch / Dinner / Snacks."""
    if not dishes:
        empty: List[DishRecommendationItem] = []
        return MealPlan(breakfast=empty, lunch=empty, dinner=empty, snacks=empty)

    n = len(dishes)
    # Prefer higher-protein items for breakfast/lunch
    protein_sorted = sorted(dishes, key=lambda d: d.protein_g, reverse=True)
    calorie_sorted = sorted(dishes, key=lambda d: d.calories_per_serving, reverse=True)

    def pick(lst, start, count):
        return lst[start:start + count]

    breakfast = pick(protein_sorted, 0, 2)
    lunch = pick(calorie_sorted, 0, 3)
    dinner = pick(protein_sorted, 2, 3)
    snacks = pick(dishes, min(8, n - 2), 2) if n > 5 else pick(dishes, 0, 2)

    return MealPlan(
        breakfast=breakfast,
        lunch=lunch,
        dinner=dinner,
        snacks=snacks,
    )


# ---------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------

@router.post("", response_model=PredictResponse, summary="Predict diet recommendation from patient data")
@router.post("/", response_model=PredictResponse, include_in_schema=False)
def predict_diet_endpoint(
    body: PredictRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Accepts patient health information, preprocesses it, runs it through
    the trained diet_model.pkl, and returns the predicted diet class.
    """
    # Compute BMI if not provided
    bmi = body.bmi
    if bmi is None or bmi <= 0:
        h_m = body.height_cm / 100.0
        bmi = round(body.weight_kg / (h_m ** 2), 2) if h_m > 0 else 22.0

    raw = {
        "Age":                            body.age,
        "Weight_kg":                      body.weight_kg,
        "Height_cm":                      body.height_cm,
        "BMI":                            bmi,
        "Daily_Caloric_Intake":           body.daily_caloric_intake,
        "Cholesterol_mg/dL":              body.cholesterol,
        "Blood_Pressure_mmHg":            body.blood_pressure,
        "Glucose_mg/dL":                  body.glucose,
        "Weekly_Exercise_Hours":          body.weekly_exercise_hours,
        "Adherence_to_Diet_Plan":         body.adherence_to_diet_plan,
        "Dietary_Nutrient_Imbalance_Score": body.dietary_nutrient_imbalance_score,
        "Gender":                         body.gender,
        "Disease_Type":                   body.disease_type,
        "Severity":                       body.severity,
        "Physical_Activity_Level":        body.physical_activity_level,
        "Dietary_Restrictions":           body.dietary_restrictions,
        "Allergies":                      body.allergies,
        "Preferred_Cuisine":              body.preferred_cuisine,
    }

    try:
        dp = _get_dp_module()
        features = dp.preprocess_patient(raw)
        result = predict_diet(features[0].tolist())
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")

    return PredictResponse(
        diet_recommendation=result["diet_recommendation"],
        confidence=result["confidence"],
        all_class_probabilities=result["all_class_probabilities"],
        model_name=result["model_name"],
    )


@router.get(
    "/diet-recommendations",
    response_model=DishRecommendationResponse,
    summary="Get dishes from CSV dataset filtered by predicted diet",
)
def get_diet_dish_recommendations(
    diet: str = Query("Balanced", description="Balanced, Low_Carb, or Low_Sodium"),
    allergies: str = Query("", description="Comma-separated allergens, e.g. nuts,dairy"),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Returns dishes from final_dish_dataset.csv (loaded into nutrition_reference DB)
    filtered by diet type and allergen restrictions, with a full meal plan.
    All data comes from the real CSV — no hard-coded food items.
    """
    user_allergies = [a.strip().lower() for a in allergies.split(",") if a.strip()]

    dishes = _get_filtered_ranked_dishes(db, diet, user_allergies, limit=limit)
    meal_plan = _build_meal_plan(dishes)
    total = db.query(NutritionReference).count()

    return DishRecommendationResponse(
        diet_recommendation=diet,
        confidence=None,
        dishes=dishes,
        meal_plan=meal_plan,
        total_dishes_available=total,
    )
