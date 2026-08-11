import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    weight = Column(Float, nullable=False)  # in kg
    height = Column(Float, nullable=False)  # in cm
    gender = Column(String, nullable=False)  # male, female, other
    activity_level = Column(String, nullable=False)  # sedentary, light, moderate, active, very_active
    goal = Column(String, nullable=False)  # lose, maintain, gain
    dietary_preferences = Column(String, default="balanced")  # balanced, vegan, vegetarian, keto, low_carb
    allergies = Column(String, default="")  # comma separated e.g. "nuts,dairy,gluten"
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    meal_logs = relationship("MealLog", back_populates="user", cascade="all, delete-orphan")
    daily_targets = relationship("DailyTarget", back_populates="user", cascade="all, delete-orphan")


class NutritionReference(Base):
    __tablename__ = "nutrition_reference"

    id = Column(Integer, primary_key=True, index=True)
    food_name = Column(String, unique=True, index=True, nullable=False)
    calories = Column(Float, nullable=False)  # per 100g
    protein = Column(Float, nullable=False)   # per 100g
    carbs = Column(Float, nullable=False)     # per 100g
    fat = Column(Float, nullable=False)       # per 100g
    serving_size_g = Column(Float, default=100.0)
    category = Column(String, default="general")
    allergens = Column(String, default="")    # e.g. "dairy,gluten"


class MealLog(Base):
    __tablename__ = "meal_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    meal_slot = Column(String, nullable=False)  # breakfast, lunch, snacks, dinner
    food_name = Column(String, nullable=False)
    calories = Column(Float, nullable=False)
    protein = Column(Float, nullable=False)
    carbs = Column(Float, nullable=False)
    fat = Column(Float, nullable=False)
    quantity_g = Column(Float, nullable=False, default=100.0)
    source = Column(String, nullable=False, default="manual")  # manual, photo
    image_url = Column(String, nullable=True)

    user = relationship("User", back_populates="meal_logs")


class DailyTarget(Base):
    __tablename__ = "daily_targets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(String, nullable=False, index=True)  # YYYY-MM-DD format
    bmr = Column(Float, nullable=False)
    target_calories = Column(Float, nullable=False)
    consumed_calories = Column(Float, default=0.0)
    remaining_calories = Column(Float, nullable=False)
    
    # Macros
    target_protein = Column(Float, default=0.0)
    target_carbs = Column(Float, default=0.0)
    target_fat = Column(Float, default=0.0)
    consumed_protein = Column(Float, default=0.0)
    consumed_carbs = Column(Float, default=0.0)
    consumed_fat = Column(Float, default=0.0)

    # Adaptive meal slot breakdown
    breakfast_target = Column(Float, default=0.0)
    lunch_target = Column(Float, default=0.0)
    snacks_target = Column(Float, default=0.0)
    dinner_target = Column(Float, default=0.0)

    breakfast_consumed = Column(Float, default=0.0)
    lunch_consumed = Column(Float, default=0.0)
    snacks_consumed = Column(Float, default=0.0)
    dinner_consumed = Column(Float, default=0.0)

    user = relationship("User", back_populates="daily_targets")
