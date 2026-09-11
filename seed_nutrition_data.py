"""
USDA FoodData Central (FDC) & Bulk Nutrition Reference Database Seeder
-----------------------------------------------------------------------
Seeds reference foods into nutrition_reference database table.
Supports USDA FDC CSV/API data structures and curated nutrition data.
"""

import sys
import os
import csv
import urllib.request
import json
from sqlalchemy.orm import Session

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from backend.app.database import engine, Base, SessionLocal
from backend.app.models import NutritionReference
from backend.app.seed_data import SEED_NUTRITION_ITEMS


def seed_usda_nutrition_data(db: Session, csv_filepath: str = None):
    """
    Populates nutrition_reference table from local USDA FDC CSV or fallback seed catalog.
    """
    print("[Seed Data] Initializing nutrition reference database seeding...")
    count_before = db.query(NutritionReference).count()
    
    # 1. Primary: Seed built-in reference dataset
    added = 0
    for item in SEED_NUTRITION_ITEMS:
        existing = db.query(NutritionReference).filter(NutritionReference.food_name == item["food_name"]).first()
        if not existing:
            ref = NutritionReference(
                food_name=item["food_name"],
                calories=item["calories"],
                protein=item["protein"],
                carbs=item["carbs"],
                fat=item["fat"],
                serving_size_g=item.get("serving_size_g", 100.0),
                category=item.get("category", "General"),
                allergens=item.get("allergens", ""),
                tags=item.get("tags", ""),
            )
            db.add(ref)
            added += 1

    # 2. Secondary: If CSV path provided (e.g. USDA FDC food.csv / nutrient.csv export)
    if csv_filepath and os.path.exists(csv_filepath):
        print(f"[Seed Data] Parsing USDA FoodData Central CSV at {csv_filepath}...")
        with open(csv_filepath, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                food_name = row.get("description") or row.get("food_name")
                if not food_name:
                    continue
                existing = db.query(NutritionReference).filter(NutritionReference.food_name == food_name).first()
                if not existing:
                    try:
                        cals = float(row.get("energy_kcal", 0.0) or row.get("calories", 0.0))
                        prot = float(row.get("protein_g", 0.0) or row.get("protein", 0.0))
                        carbs = float(row.get("carbohydrate_g", 0.0) or row.get("carbs", 0.0))
                        fat = float(row.get("fat_g", 0.0) or row.get("fat", 0.0))
                        ref = NutritionReference(
                            food_name=food_name,
                            calories=cals,
                            protein=prot,
                            carbs=carbs,
                            fat=fat,
                            serving_size_g=100.0,
                            category=row.get("food_category", "USDA FDC"),
                            allergens="",
                            tags="usda_fdc",
                        )
                        db.add(ref)
                        added += 1
                    except ValueError:
                        continue

    db.commit()
    count_after = db.query(NutritionReference).count()
    print(f"[Seed Data] Finished. Added {added} new reference items. Total items in DB: {count_after}")


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        csv_path = sys.argv[1] if len(sys.argv) > 1 else None
        seed_usda_nutrition_data(db, csv_filepath=csv_path)
    finally:
        db.close()
