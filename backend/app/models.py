import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from backend.app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    weight = Column(Float, nullable=False)  # in kg (weight_kg)
    height = Column(Float, nullable=False)  # in cm (height_cm)
    gender = Column(String, nullable=False)  # male, female, other
    activity_level = Column(String, nullable=False)  # sedentary, light, moderate, active, very_active
    goal = Column(String, nullable=False)  # lose, maintain, gain
    dietary_preferences = Column(String, default="balanced")  # balanced, vegan, vegetarian, keto, low_carb
    allergies = Column(String, default="")  # comma separated e.g. "nuts,dairy,gluten"
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    meal_slots = relationship("MealSlot", back_populates="user", cascade="all, delete-orphan")
    meal_logs = relationship("MealLog", back_populates="user", cascade="all, delete-orphan")
    daily_targets = relationship("DailyTarget", back_populates="user", cascade="all, delete-orphan")

    @property
    def weight_kg(self) -> float:
        return self.weight

    @property
    def height_cm(self) -> float:
        return self.height

    @property
    def hashed_password(self) -> str:
        return self.password_hash


class MealSlot(Base):
    __tablename__ = "meal_slots"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)  # breakfast, lunch, snack, dinner
    default_weight_pct = Column(Float, nullable=False)  # e.g. 25.0 for 25%

    user = relationship("User", back_populates="meal_slots")


class NutritionReference(Base):
    __tablename__ = "nutrition_reference"

    id = Column(Integer, primary_key=True, index=True)
    food_name = Column(String, unique=True, index=True, nullable=False)
    calories = Column(Float, nullable=False)  # per 100g (calories_per_100g)
    protein = Column(Float, nullable=False)   # per 100g
    carbs = Column(Float, nullable=False)     # per 100g
    fat = Column(Float, nullable=False)       # per 100g
    serving_size_g = Column(Float, default=100.0)
    category = Column(String, default="general")
    allergens = Column(String, default="")    # e.g. "dairy,gluten"
    tags = Column(String, default="")         # e.g. "vegetarian,vegan"

    @property
    def calories_per_100g(self) -> float:
        return self.calories

    @property
    def common_allergens(self) -> list:
        return [a.strip() for a in (self.allergens or "").split(",") if a.strip()]


class MealLog(Base):
    __tablename__ = "meal_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    meal_slot_id = Column(Integer, ForeignKey("meal_slots.id"), nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    meal_slot = Column(String, nullable=False)  # breakfast, lunch, snack, dinner
    food_name = Column(String, nullable=False)
    quantity_g = Column(Float, nullable=False, default=100.0)
    calories = Column(Float, nullable=False)
    protein_g = Column(Float, nullable=False, default=0.0)
    carbs_g = Column(Float, nullable=False, default=0.0)
    fat_g = Column(Float, nullable=False, default=0.0)
    source = Column(String, nullable=False, default="manual")  # manual, photo
    confidence_score = Column(Float, nullable=True)  # nullable, 0-1
    image_url = Column(String, nullable=True)

    user = relationship("User", back_populates="meal_logs")

    @property
    def protein(self) -> float:
        return self.protein_g

    @protein.setter
    def protein(self, val: float):
        self.protein_g = val

    @property
    def carbs(self) -> float:
        return self.carbs_g

    @carbs.setter
    def carbs(self, val: float):
        self.carbs_g = val

    @property
    def fat(self) -> float:
        return self.fat_g

    @fat.setter
    def fat(self, val: float):
        self.fat_g = val


class DailyTarget(Base):
    __tablename__ = "daily_targets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(String, nullable=False, index=True)  # YYYY-MM-DD format
    bmr = Column(Float, nullable=False)
    target_calories = Column(Float, nullable=False)
    consumed_calories = Column(Float, default=0.0)
    remaining_calories = Column(Float, nullable=False)
    slot_targets = Column(JSON, nullable=True)  # JSON: {slot_name: target_kcal}
    
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

