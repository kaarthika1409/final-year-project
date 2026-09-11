"""
seed_data.py
============
Seeds the nutrition_reference database table from final_dish_dataset.csv
(4,768 real dishes). The seeding only runs when the table is empty.

The mock 44 hard-coded food items have been replaced with the actual dataset.
"""

import os
import logging
import pandas as pd
from sqlalchemy.orm import Session
from backend.app.models import NutritionReference

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------
# Paths
# ---------------------------------------------------------------
_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DISH_CSV = os.path.join(_BACKEND_DIR, "data", "final_dish_dataset.csv")

# ---------------------------------------------------------------
# Allergen keyword detection from ingredient name
# ---------------------------------------------------------------
_ALLERGEN_MAP = {
    "nuts":      ["almond", "walnut", "cashew", "hazelnut", "pecan", "pistachio", "macadamia", "nut"],
    "peanuts":   ["peanut", "groundnut"],
    "dairy":     ["milk", "cheese", "butter", "cream", "yogurt", "ghee", "whey", "lactose"],
    "gluten":    ["wheat", "bread", "flour", "pasta", "barley", "rye", "semolina", "noodle"],
    "eggs":      ["egg"],
    "shellfish": ["shrimp", "prawn", "crab", "lobster", "crayfish", "scallop", "oyster", "clam"],
    "fish":      ["salmon", "tuna", "cod", "tilapia", "halibut", "anchov", "sardine", "fish"],
    "soy":       ["soy", "tofu", "miso", "tempeh", "edamame"],
    "sesame":    ["sesame", "tahini"],
}


def _derive_allergens(ingredient_list: str) -> str:
    """Derive allergens string from comma-joined ingredient names."""
    ingr_lower = ingredient_list.lower()
    found = []
    for allergen, keywords in _ALLERGEN_MAP.items():
        if any(kw in ingr_lower for kw in keywords):
            found.append(allergen)
    return ",".join(found)


def _derive_category(top_ingredient: str) -> str:
    """Map dominant ingredient to a broad food category."""
    ing = top_ingredient.lower().strip()
    if any(k in ing for k in ["chicken", "turkey", "duck", "hen"]):
        return "Poultry"
    if any(k in ing for k in ["beef", "pork", "lamb", "veal", "bacon", "steak", "meat"]):
        return "Meat"
    if any(k in ing for k in ["salmon", "tuna", "cod", "fish", "shrimp", "prawn", "crab", "seafood", "lobster"]):
        return "Seafood"
    if any(k in ing for k in ["rice", "pasta", "noodle", "wheat", "bread", "flour", "oat", "grain", "barley"]):
        return "Grains"
    if any(k in ing for k in ["milk", "cheese", "yogurt", "cream", "butter", "dairy"]):
        return "Dairy"
    if any(k in ing for k in ["egg"]):
        return "Eggs"
    if any(k in ing for k in ["tofu", "soy", "tempeh", "bean", "lentil", "legume", "chickpea"]):
        return "Plant Protein"
    if any(k in ing for k in ["almond", "walnut", "cashew", "nut", "peanut", "pistachio", "seed"]):
        return "Nuts & Seeds"
    if any(k in ing for k in ["apple", "banana", "mango", "berry", "fruit", "grape", "orange", "lemon"]):
        return "Fruit"
    if any(k in ing for k in ["spinach", "kale", "broccoli", "carrot", "onion", "potato", "tomato",
                               "lettuce", "cucumber", "pepper", "celery", "mushroom", "vegetable"]):
        return "Vegetables"
    if any(k in ing for k in ["oil", "olive", "coconut", "avocado"]):
        return "Fats & Oils"
    return "Mixed Dish"


def seed_nutrition_database(db: Session):
    """
    Populates nutrition_reference table with dishes from final_dish_dataset.csv.
    Only runs if the table is empty — safe to call on every startup.
    """
    existing_count = db.query(NutritionReference).count()
    if existing_count > 0:
        logger.info(f"nutrition_reference already has {existing_count} rows — skipping seed.")
        return

    if not os.path.exists(_DISH_CSV):
        logger.warning(f"Dish CSV not found at {_DISH_CSV} — falling back to empty DB.")
        return

    logger.info(f"Seeding nutrition_reference from {_DISH_CSV} ...")

    try:
        df = pd.read_csv(_DISH_CSV)

        # Aggregate: one row per dish_id
        # Ingredients: join all ingr_name values for that dish
        agg = (
            df.groupby("dish_id")
            .agg(
                ingr_name=("ingr_name", lambda x: ", ".join(x.dropna().astype(str))),
                total_calories=("total_calories", "first"),
                total_fat=("total_fat", "first"),
                total_carbohydrates=("total_carbohydrates", "first"),
                total_protein=("total_protein", "first"),
                total_grams=("total_grams", "first"),
                calories_per_100g=("calories_per_100g", "first"),
                fat_per_100g=("fat_per_100g", "first"),
                carbohydrates_per_100g=("carbohydrates_per_100g", "first"),
                protein_per_100g=("protein_per_100g", "first"),
            )
            .reset_index()
        )

        # First ingredient as top-level category signal
        first_ingr = df.groupby("dish_id")["ingr_name"].first().reset_index()
        first_ingr.columns = ["dish_id", "top_ingredient"]
        agg = agg.merge(first_ingr, on="dish_id")

        records = []
        seen_names = set()

        for _, row in agg.iterrows():
            top_ingr = str(row["top_ingredient"]).strip()
            ingr_list = str(row["ingr_name"])

            # Human-readable name: "Dish - <top ingredient>"
            food_name = f"Dish - {top_ingr.title()}"

            # Deduplicate (in case two dishes share the same top ingredient name)
            if food_name in seen_names:
                food_name = f"{food_name} ({row['dish_id']})"
            seen_names.add(food_name)

            allergens = _derive_allergens(ingr_list)
            category = _derive_category(top_ingr)

            # Use per-100g values for calorie/macro fields (model stores per-100g)
            cal_100 = row["calories_per_100g"] if pd.notna(row["calories_per_100g"]) and row["calories_per_100g"] > 0 else (
                (row["total_calories"] / row["total_grams"] * 100) if row["total_grams"] > 0 else 0.0
            )
            fat_100 = row["fat_per_100g"] if pd.notna(row["fat_per_100g"]) else 0.0
            carb_100 = row["carbohydrates_per_100g"] if pd.notna(row["carbohydrates_per_100g"]) else 0.0
            prot_100 = row["protein_per_100g"] if pd.notna(row["protein_per_100g"]) else 0.0
            serving = row["total_grams"] if pd.notna(row["total_grams"]) and row["total_grams"] > 0 else 100.0

            records.append(
                NutritionReference(
                    food_name=food_name,
                    calories=round(float(cal_100), 2),
                    protein=round(float(prot_100), 2),
                    carbs=round(float(carb_100), 2),
                    fat=round(float(fat_100), 2),
                    serving_size_g=round(float(serving), 1),
                    category=category,
                    allergens=allergens,
                    tags=ingr_list[:500],  # Store ingredient list in tags (truncated)
                )
            )

        # Batch insert in chunks to avoid memory issues
        CHUNK = 500
        for i in range(0, len(records), CHUNK):
            db.bulk_save_objects(records[i : i + CHUNK])
            db.commit()

        logger.info(f"Seeded {len(records)} dishes from final_dish_dataset.csv into nutrition_reference.")

    except Exception as e:
        logger.error(f"Failed to seed nutrition database from CSV: {e}")
        db.rollback()
