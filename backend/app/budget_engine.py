def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    """
    Calculates Basal Metabolic Rate (BMR) using Mifflin-St Jeor equation.
    Male: (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
    Female: (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
    """
    base = (10.0 * weight_kg) + (6.25 * height_cm) - (5.0 * age)
    gender_lower = gender.lower()
    if gender_lower == "male":
        return round(base + 5.0, 2)
    elif gender_lower == "female":
        return round(base - 161.0, 2)
    else:
        # Default midpoint for non-binary / other
        return round(base - 78.0, 2)


def get_activity_multiplier(activity_level: str) -> float:
    multipliers = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9,
    }
    return multipliers.get(activity_level.lower(), 1.2)


def get_goal_adjustment(goal: str) -> float:
    adjustments = {
        "lose": -500.0,
        "maintain": 0.0,
        "gain": 500.0,
    }
    return adjustments.get(goal.lower(), 0.0)


def calculate_daily_calorie_target(
    weight_kg: float, height_cm: float, age: int, gender: str, activity_level: str, goal: str
) -> dict:
    bmr = calculate_bmr(weight_kg, height_cm, age, gender)
    multiplier = get_activity_multiplier(activity_level)
    tdee = round(bmr * multiplier, 1)
    adjustment = get_goal_adjustment(goal)
    target_calories = max(1200.0, round(tdee + adjustment, 1))  # Ensure a safe minimum threshold

    # Calculate recommended macro split
    target_protein = round((target_calories * 0.30) / 4.0, 1)  # 30% protein (4 kcal/g)
    target_carbs = round((target_calories * 0.45) / 4.0, 1)    # 45% carbs (4 kcal/g)
    target_fat = round((target_calories * 0.25) / 9.0, 1)      # 25% fat (9 kcal/g)

    return {
        "bmr": bmr,
        "tdee": tdee,
        "target_calories": target_calories,
        "target_protein": target_protein,
        "target_carbs": target_carbs,
        "target_fat": target_fat,
    }


def calculate_bmi(weight_kg: float, height_cm: float) -> dict:
    height_m = height_cm / 100.0
    if height_m <= 0:
        return {"bmi": 0.0, "category": "Unknown"}
    bmi = round(weight_kg / (height_m ** 2), 1)

    if bmi < 18.5:
        category = "Underweight"
    elif 18.5 <= bmi < 25.0:
        category = "Normal"
    elif 25.0 <= bmi < 30.0:
        category = "Overweight"
    else:
        category = "Obese"

    return {"bmi": bmi, "category": category}
