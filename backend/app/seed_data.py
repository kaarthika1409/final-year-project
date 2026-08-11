from sqlalchemy.orm import Session
from backend.app.models import NutritionReference

SEED_NUTRITION_ITEMS = [
    {"food_name": "Apple", "calories": 52.0, "protein": 0.3, "carbs": 13.8, "fat": 0.2, "serving_size_g": 150.0, "category": "Fruit", "allergens": ""},
    {"food_name": "Banana", "calories": 89.0, "protein": 1.1, "carbs": 22.8, "fat": 0.3, "serving_size_g": 120.0, "category": "Fruit", "allergens": ""},
    {"food_name": "Orange", "calories": 47.0, "protein": 0.9, "carbs": 11.8, "fat": 0.1, "serving_size_g": 140.0, "category": "Fruit", "allergens": ""},
    {"food_name": "Blueberries", "calories": 57.0, "protein": 0.7, "carbs": 14.5, "fat": 0.3, "serving_size_g": 100.0, "category": "Fruit", "allergens": ""},
    {"food_name": "Avocado", "calories": 160.0, "protein": 2.0, "carbs": 8.5, "fat": 14.7, "serving_size_g": 150.0, "category": "Fruit", "allergens": ""},
    
    {"food_name": "Grilled Chicken Breast", "calories": 165.0, "protein": 31.0, "carbs": 0.0, "fat": 3.6, "serving_size_g": 150.0, "category": "Poultry", "allergens": ""},
    {"food_name": "Turkey Breast", "calories": 135.0, "protein": 30.0, "carbs": 0.0, "fat": 1.0, "serving_size_g": 150.0, "category": "Poultry", "allergens": ""},
    {"food_name": "Grilled Salmon", "calories": 206.0, "protein": 22.0, "carbs": 0.0, "fat": 12.3, "serving_size_g": 150.0, "category": "Seafood", "allergens": "fish"},
    {"food_name": "Tuna Steak", "calories": 130.0, "protein": 28.0, "carbs": 0.0, "fat": 1.2, "serving_size_g": 150.0, "category": "Seafood", "allergens": "fish"},
    {"food_name": "Shrimp", "calories": 99.0, "protein": 24.0, "carbs": 0.2, "fat": 0.3, "serving_size_g": 120.0, "category": "Seafood", "allergens": "shellfish"},
    {"food_name": "Beef Steak (Ribeye)", "calories": 271.0, "protein": 25.0, "carbs": 0.0, "fat": 19.0, "serving_size_g": 200.0, "category": "Meat", "allergens": ""},
    {"food_name": "Boiled Eggs", "calories": 155.0, "protein": 12.6, "carbs": 1.1, "fat": 10.6, "serving_size_g": 100.0, "category": "Eggs", "allergens": "eggs"},
    {"food_name": "Tofu (Firm)", "calories": 76.0, "protein": 8.0, "carbs": 1.9, "fat": 4.8, "serving_size_g": 150.0, "category": "Vegan Protein", "allergens": "soy"},
    
    {"food_name": "Brown Rice", "calories": 111.0, "protein": 2.6, "carbs": 23.0, "fat": 0.9, "serving_size_g": 150.0, "category": "Grains", "allergens": ""},
    {"food_name": "White Rice", "calories": 130.0, "protein": 2.7, "carbs": 28.0, "fat": 0.3, "serving_size_g": 150.0, "category": "Grains", "allergens": ""},
    {"food_name": "Oatmeal (Cooked)", "calories": 71.0, "protein": 2.5, "carbs": 12.0, "fat": 1.5, "serving_size_g": 200.0, "category": "Grains", "allergens": "gluten"},
    {"food_name": "Quinoa", "calories": 120.0, "protein": 4.4, "carbs": 21.3, "fat": 1.9, "serving_size_g": 150.0, "category": "Grains", "allergens": ""},
    {"food_name": "Sweet Potato (Baked)", "calories": 90.0, "protein": 2.0, "carbs": 20.7, "fat": 0.1, "serving_size_g": 150.0, "category": "Vegetables", "allergens": ""},
    {"food_name": "Whole Wheat Bread", "calories": 247.0, "protein": 13.0, "carbs": 41.0, "fat": 3.4, "serving_size_g": 70.0, "category": "Grains", "allergens": "gluten"},
    {"food_name": "Whole Wheat Pasta", "calories": 124.0, "protein": 5.3, "carbs": 25.0, "fat": 0.5, "serving_size_g": 180.0, "category": "Grains", "allergens": "gluten"},

    {"food_name": "Greek Yogurt (Non-fat)", "calories": 59.0, "protein": 10.0, "carbs": 3.6, "fat": 0.4, "serving_size_g": 170.0, "category": "Dairy", "allergens": "dairy"},
    {"food_name": "Cottage Cheese", "calories": 98.0, "protein": 11.0, "carbs": 3.4, "fat": 4.3, "serving_size_g": 150.0, "category": "Dairy", "allergens": "dairy"},
    {"food_name": "Cheddar Cheese", "calories": 403.0, "protein": 24.9, "carbs": 1.3, "fat": 33.1, "serving_size_g": 30.0, "category": "Dairy", "allergens": "dairy"},
    {"food_name": "Almonds", "calories": 579.0, "protein": 21.2, "carbs": 21.6, "fat": 49.9, "serving_size_g": 30.0, "category": "Nuts", "allergens": "nuts"},
    {"food_name": "Peanut Butter", "calories": 588.0, "protein": 25.0, "carbs": 20.0, "fat": 50.0, "serving_size_g": 32.0, "category": "Nuts", "allergens": "nuts,peanuts"},
    {"food_name": "Walnuts", "calories": 654.0, "protein": 15.2, "carbs": 13.7, "fat": 65.2, "serving_size_g": 30.0, "category": "Nuts", "allergens": "nuts"},

    {"food_name": "Broccoli (Steamed)", "calories": 35.0, "protein": 2.4, "carbs": 7.2, "fat": 0.4, "serving_size_g": 150.0, "category": "Vegetables", "allergens": ""},
    {"food_name": "Spinach (Fresh)", "calories": 23.0, "protein": 2.9, "carbs": 3.6, "fat": 0.4, "serving_size_g": 100.0, "category": "Vegetables", "allergens": ""},
    {"food_name": "Caesar Salad", "calories": 140.0, "protein": 3.5, "carbs": 6.0, "fat": 11.5, "serving_size_g": 200.0, "category": "Salad", "allergens": "dairy,gluten,eggs"},
    {"food_name": "Greek Salad", "calories": 110.0, "protein": 3.0, "carbs": 5.5, "fat": 8.5, "serving_size_g": 200.0, "category": "Salad", "allergens": "dairy"},
    {"food_name": "Garden Salad", "calories": 30.0, "protein": 1.5, "carbs": 5.0, "fat": 0.5, "serving_size_g": 150.0, "category": "Salad", "allergens": ""},
    {"food_name": "Hummus", "calories": 166.0, "protein": 7.9, "carbs": 14.3, "fat": 9.6, "serving_size_g": 50.0, "category": "Vegan", "allergens": "sesame"},

    {"food_name": "Pizza (Pepperoni Slice)", "calories": 266.0, "protein": 11.0, "carbs": 30.0, "fat": 11.5, "serving_size_g": 110.0, "category": "Dishes", "allergens": "dairy,gluten"},
    {"food_name": "Cheeseburger", "calories": 303.0, "protein": 15.0, "carbs": 30.0, "fat": 14.0, "serving_size_g": 160.0, "category": "Dishes", "allergens": "dairy,gluten"},
    {"food_name": "Chicken Wings (4 pcs)", "calories": 290.0, "protein": 23.0, "carbs": 0.0, "fat": 21.0, "serving_size_g": 150.0, "category": "Poultry", "allergens": ""},
    {"food_name": "Chicken Burrito Bowl", "calories": 160.0, "protein": 12.0, "carbs": 18.0, "fat": 5.0, "serving_size_g": 350.0, "category": "Dishes", "allergens": "dairy"},
    {"food_name": "Sushi Roll (California)", "calories": 140.0, "protein": 3.5, "carbs": 26.0, "fat": 2.0, "serving_size_g": 180.0, "category": "Seafood", "allergens": "fish,soy"},
    {"food_name": "Steamed Dumplings (6 pcs)", "calories": 180.0, "protein": 8.0, "carbs": 24.0, "fat": 6.0, "serving_size_g": 150.0, "category": "Dishes", "allergens": "gluten,soy"},
    {"food_name": "Ramen Noodle Soup", "calories": 110.0, "protein": 4.5, "carbs": 15.0, "fat": 4.0, "serving_size_g": 400.0, "category": "Dishes", "allergens": "gluten,soy,eggs"},
    {"food_name": "Falafel Wrap", "calories": 190.0, "protein": 6.5, "carbs": 28.0, "fat": 7.0, "serving_size_g": 220.0, "category": "Vegan", "allergens": "gluten,sesame"},

    {"food_name": "Whey Protein Shake", "calories": 120.0, "protein": 24.0, "carbs": 3.0, "fat": 1.5, "serving_size_g": 300.0, "category": "Supplements", "allergens": "dairy"},
    {"food_name": "Plant-Based Protein Shake", "calories": 130.0, "protein": 22.0, "carbs": 4.0, "fat": 2.5, "serving_size_g": 300.0, "category": "Supplements", "allergens": "soy"},
    {"food_name": "Dark Chocolate (70%)", "calories": 598.0, "protein": 7.8, "carbs": 45.9, "fat": 42.6, "serving_size_g": 30.0, "category": "Snacks", "allergens": "dairy"},
    {"food_name": "French Fries", "calories": 312.0, "protein": 3.4, "carbs": 41.0, "fat": 15.0, "serving_size_g": 120.0, "category": "Snacks", "allergens": ""},
    {"food_name": "Pancakes with Maple Syrup", "calories": 227.0, "protein": 6.0, "carbs": 45.0, "fat": 3.0, "serving_size_g": 150.0, "category": "Breakfast", "allergens": "gluten,eggs,dairy"},
]


def seed_nutrition_database(db: Session):
    """Populates nutrition_reference table if empty."""
    existing_count = db.query(NutritionReference).count()
    if existing_count == 0:
        for item in SEED_NUTRITION_ITEMS:
            record = NutritionReference(
                food_name=item["food_name"],
                calories=item["calories"],
                protein=item["protein"],
                carbs=item["carbs"],
                fat=item["fat"],
                serving_size_g=item["serving_size_g"],
                category=item["category"],
                allergens=item["allergens"],
            )
            db.add(record)
        db.commit()
