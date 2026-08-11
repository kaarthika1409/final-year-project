from typing import List
from sqlalchemy.orm import Session
from backend.app.models import NutritionReference, User, DailyTarget
from backend.app.schemas import RecommendationItem, RecommendationResponse


NON_VEGETARIAN_CATEGORIES = ["meat", "poultry", "seafood", "fish"]
NON_VEGAN_CATEGORIES = ["meat", "poultry", "seafood", "fish", "dairy", "eggs"]


def get_dietary_recommendations(
    user: User, target: DailyTarget, db: Session, limit: int = 5
) -> RecommendationResponse:
    remaining_calories = max(50.0, target.remaining_calories)
    remaining_protein = max(0.0, target.target_protein - target.consumed_protein)
    remaining_carbs = max(0.0, target.target_carbs - target.consumed_carbs)
    remaining_fat = max(0.0, target.target_fat - target.consumed_fat)

    user_allergies = [a.strip().lower() for a in user.allergies.split(",") if a.strip()]
    pref = (user.dietary_preferences or "balanced").lower()

    # Query all nutrition reference items
    all_foods = db.query(NutritionReference).all()
    scored_items: List[tuple[float, NutritionReference, str]] = []

    for food in all_foods:
        # 1. Allergy check
        food_allergens = [a.strip().lower() for a in (food.allergens or "").split(",") if a.strip()]
        if any(allergen in food_allergens for allergen in user_allergies):
            continue

        # 2. Preference check
        category = (food.category or "").lower()
        if pref == "vegan" and (category in NON_VEGAN_CATEGORIES or any(item in food.food_name.lower() for item in ["egg", "milk", "cheese", "yogurt", "chicken", "beef", "fish", "salmon", "turkey"])):
            continue
        elif pref == "vegetarian" and (category in NON_VEGETARIAN_CATEGORIES or any(item in food.food_name.lower() for item in ["chicken", "beef", "fish", "salmon", "turkey", "pork"])):
            continue
        elif pref == "keto" and food.carbs > 15.0:
            continue

        # Serving calculation (default standard serving size or 100g)
        serving_g = food.serving_size_g or 100.0
        portion_factor = serving_g / 100.0
        item_calories = food.calories * portion_factor
        item_protein = food.protein * portion_factor
        item_carbs = food.carbs * portion_factor
        item_fat = food.fat * portion_factor

        # 3. Calorie fit scoring
        # Reward items that fill a good fraction of remaining calories without massively exceeding
        if item_calories > (remaining_calories + 200.0):
            continue  # Too heavy for remaining budget

        calorie_ratio = item_calories / remaining_calories if remaining_calories > 0 else 0.5
        calorie_score = 1.0 - abs(calorie_ratio - 0.4)  # Ideal single snack/meal is 30-50% of remaining

        # 4. Macro alignment scoring
        protein_score = (item_protein / (remaining_protein + 1.0)) * 1.5 if remaining_protein > 0 else 0.5
        
        total_score = (calorie_score * 0.4) + (protein_score * 0.6)

        # Fit description
        reasons = []
        if item_protein >= 15.0:
            reasons.append("High protein")
        if item_carbs <= 10.0:
            reasons.append("Low carb")
        if abs(item_calories - remaining_calories * 0.35) < 100:
            reasons.append("Optimal calorie fit")
        if not reasons:
            reasons.append("Nutritionally balanced choice")
        fit_reason = ", ".join(reasons)

        scored_items.append((total_score, food, fit_reason))

    # Sort descending by score
    scored_items.sort(key=lambda x: x[0], reverse=True)
    top_matches = scored_items[:limit]

    suggestions = []
    for score, food, reason in top_matches:
        serving_g = food.serving_size_g or 100.0
        portion_factor = serving_g / 100.0
        suggestions.append(
            RecommendationItem(
                id=food.id,
                food_name=food.food_name,
                category=food.category or "General",
                calories_per_serving=round(food.calories * portion_factor, 1),
                protein_g=round(food.protein * portion_factor, 1),
                carbs_g=round(food.carbs * portion_factor, 1),
                fat_g=round(food.fat * portion_factor, 1),
                serving_size_g=serving_g,
                fit_reason=reason,
                match_score=round(max(0.1, min(1.0, score)), 2),
            )
        )

    return RecommendationResponse(
        remaining_calories=round(remaining_calories, 1),
        remaining_protein=round(remaining_protein, 1),
        remaining_carbs=round(remaining_carbs, 1),
        remaining_fat=round(remaining_fat, 1),
        suggestions=suggestions,
    )
