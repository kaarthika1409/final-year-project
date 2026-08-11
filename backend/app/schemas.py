from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, EmailStr, Field


# --- Auth Schemas ---
class UserSignup(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    age: int = Field(..., ge=1, le=120)
    weight: float = Field(..., gt=0)  # kg
    height: float = Field(..., gt=0)  # cm
    gender: str = Field(..., pattern="^(male|female|other)$")
    activity_level: str = Field(..., pattern="^(sedentary|light|moderate|active|very_active)$")
    goal: str = Field(..., pattern="^(lose|maintain|gain)$")
    dietary_preferences: Optional[str] = "balanced"
    allergies: Optional[str] = ""


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    age: Optional[int] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    gender: Optional[str] = None
    activity_level: Optional[str] = None
    goal: Optional[str] = None
    dietary_preferences: Optional[str] = None
    allergies: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    email: str
    age: int
    weight: float
    height: float
    gender: str
    activity_level: str
    goal: str
    dietary_preferences: str
    allergies: str
    bmr: Optional[float] = None
    tdee: Optional[float] = None
    daily_calorie_target: Optional[float] = None
    bmi: Optional[float] = None
    bmi_category: Optional[str] = None

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# --- Meal Schemas ---
class MealLogCreate(BaseModel):
    meal_slot: str = Field(..., pattern="^(breakfast|lunch|snacks|dinner)$")
    food_name: str
    quantity_g: float = Field(..., gt=0)
    source: str = "manual"
    image_url: Optional[str] = None


class MealLogResponse(BaseModel):
    id: int
    user_id: int
    timestamp: datetime
    meal_slot: str
    food_name: str
    calories: float
    protein: float
    carbs: float
    fat: float
    quantity_g: float
    source: str
    image_url: Optional[str] = None

    model_config = {"from_attributes": True}


class PhotoDetectRequest(BaseModel):
    image_base64: Optional[str] = None
    meal_slot: str = "lunch"


class PhotoDetectResponse(BaseModel):
    detected_food: str
    confidence: float
    portion_g: float
    calories: float
    protein: float
    carbs: float
    fat: float
    match_source: str
    image_url: Optional[str] = None


# --- Target / Redistribution Schemas ---
class MealSlotBreakdown(BaseModel):
    target: float
    consumed: float
    remaining: float


class DailyTargetResponse(BaseModel):
    id: int
    user_id: int
    date: str
    bmr: float
    target_calories: float
    consumed_calories: float
    remaining_calories: float
    target_protein: float
    target_carbs: float
    target_fat: float
    consumed_protein: float
    consumed_carbs: float
    consumed_fat: float
    remaining_protein: float
    remaining_carbs: float
    remaining_fat: float
    breakfast: MealSlotBreakdown
    lunch: MealSlotBreakdown
    snacks: MealSlotBreakdown
    dinner: MealSlotBreakdown

    model_config = {"from_attributes": True}


# --- Recommendation Schemas ---
class RecommendationItem(BaseModel):
    id: int
    food_name: str
    category: str
    calories_per_serving: float
    protein_g: float
    carbs_g: float
    fat_g: float
    serving_size_g: float
    fit_reason: str
    match_score: float


class RecommendationResponse(BaseModel):
    remaining_calories: float
    remaining_protein: float
    remaining_carbs: float
    remaining_fat: float
    suggestions: List[RecommendationItem]


# --- Accuracy Evaluation Schemas ---
class GroupAccuracyResult(BaseModel):
    group_type: str  # age, gender, bmi
    group_name: str
    sample_count: int
    mae: float
    rmse: float
    avg_actual: float
    avg_predicted: float


class AccuracyReportResponse(BaseModel):
    total_users: int
    overall_mae: float
    overall_rmse: float
    group_metrics: List[GroupAccuracyResult]
