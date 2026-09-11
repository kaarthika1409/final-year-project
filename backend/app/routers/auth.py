from typing import Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import User, MealSlot
from backend.app.schemas import UserSignup, UserLogin, UserResponse, UserUpdate, Token
from backend.app.security import get_password_hash, verify_password, create_access_token, get_current_user
from backend.app.budget_engine import calculate_daily_calorie_target, calculate_bmi

router = APIRouter(tags=["User Auth & Calorie Budget"])


class CalorieBudgetCalculateRequest(BaseModel):
    weight_kg: float = Field(..., gt=0)
    height_cm: float = Field(..., gt=0)
    age: int = Field(..., ge=1, le=120)
    gender: str = Field(..., pattern="^(male|female|other)$")
    activity_level: str = Field(..., pattern="^(sedentary|light|moderate|active|very_active)$")
    goal: str = Field(..., pattern="^(lose|maintain|gain)$")
    goal_delta_kcal: Optional[float] = 500.0


def create_default_meal_slots(user_id: int, db: Session):
    defaults = [
        {"name": "breakfast", "default_weight_pct": 25.0},
        {"name": "lunch", "default_weight_pct": 35.0},
        {"name": "snack", "default_weight_pct": 10.0},
        {"name": "dinner", "default_weight_pct": 30.0},
    ]
    for slot_def in defaults:
        slot = MealSlot(
            user_id=user_id,
            name=slot_def["name"],
            default_weight_pct=slot_def["default_weight_pct"],
        )
        db.add(slot)
    db.commit()


@router.post("/api/auth/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
@router.post("/auth/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
def signup(user_in: UserSignup, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered. Please login.",
        )

    hashed_pw = get_password_hash(user_in.password)
    new_user = User(
        email=user_in.email,
        password_hash=hashed_pw,
        age=user_in.age,
        weight=user_in.weight,
        height=user_in.height,
        gender=user_in.gender,
        activity_level=user_in.activity_level,
        goal=user_in.goal,
        dietary_preferences=user_in.dietary_preferences or "balanced",
        allergies=user_in.allergies or "",
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    create_default_meal_slots(new_user.id, db)

    access_token = create_access_token(data={"sub": new_user.email})

    budget = calculate_daily_calorie_target(
        new_user.weight, new_user.height, new_user.age, new_user.gender, new_user.activity_level, new_user.goal
    )
    bmi_info = calculate_bmi(new_user.weight, new_user.height)

    user_resp = UserResponse(
        id=new_user.id,
        email=new_user.email,
        age=new_user.age,
        weight=new_user.weight,
        height=new_user.height,
        gender=new_user.gender,
        activity_level=new_user.activity_level,
        goal=new_user.goal,
        dietary_preferences=new_user.dietary_preferences,
        allergies=new_user.allergies,
        bmr=budget["bmr"],
        tdee=budget["tdee"],
        daily_calorie_target=budget["target_calories"],
        bmi=bmi_info["bmi"],
        bmi_category=bmi_info["category"],
    )

    return Token(access_token=access_token, token_type="bearer", user=user_resp)


@router.post("/api/auth/login", response_model=Token)
@router.post("/auth/login", response_model=Token)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_in.email).first()
    if not user or not verify_password(user_in.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token = create_access_token(data={"sub": user.email})

    budget = calculate_daily_calorie_target(
        user.weight, user.height, user.age, user.gender, user.activity_level, user.goal
    )
    bmi_info = calculate_bmi(user.weight, user.height)

    user_resp = UserResponse(
        id=user.id,
        email=user.email,
        age=user.age,
        weight=user.weight,
        height=user.height,
        gender=user.gender,
        activity_level=user.activity_level,
        goal=user.goal,
        dietary_preferences=user.dietary_preferences,
        allergies=user.allergies,
        bmr=budget["bmr"],
        tdee=budget["tdee"],
        daily_calorie_target=budget["target_calories"],
        bmi=bmi_info["bmi"],
        bmi_category=bmi_info["category"],
    )

    return Token(access_token=access_token, token_type="bearer", user=user_resp)


@router.get("/api/auth/me", response_model=UserResponse)
@router.get("/auth/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    budget = calculate_daily_calorie_target(
        current_user.weight, current_user.height, current_user.age, current_user.gender, current_user.activity_level, current_user.goal
    )
    bmi_info = calculate_bmi(current_user.weight, current_user.height)

    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        age=current_user.age,
        weight=current_user.weight,
        height=current_user.height,
        gender=current_user.gender,
        activity_level=current_user.activity_level,
        goal=current_user.goal,
        dietary_preferences=current_user.dietary_preferences,
        allergies=current_user.allergies,
        bmr=budget["bmr"],
        tdee=budget["tdee"],
        daily_calorie_target=budget["target_calories"],
        bmi=bmi_info["bmi"],
        bmi_category=bmi_info["category"],
    )


@router.put("/api/auth/profile", response_model=UserResponse)
def update_profile(
    user_update: UserUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    for field, val in user_update.model_dump(exclude_unset=True).items():
        if val is not None:
            setattr(current_user, field, val)

    db.commit()
    db.refresh(current_user)

    budget = calculate_daily_calorie_target(
        current_user.weight, current_user.height, current_user.age, current_user.gender, current_user.activity_level, current_user.goal
    )
    bmi_info = calculate_bmi(current_user.weight, current_user.height)

    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        age=current_user.age,
        weight=current_user.weight,
        height=current_user.height,
        gender=current_user.gender,
        activity_level=current_user.activity_level,
        goal=current_user.goal,
        dietary_preferences=current_user.dietary_preferences,
        allergies=current_user.allergies,
        bmr=budget["bmr"],
        tdee=budget["tdee"],
        daily_calorie_target=budget["target_calories"],
        bmi=bmi_info["bmi"],
        bmi_category=bmi_info["category"],
    )


@router.post("/calorie-budget/calculate")
@router.post("/api/calorie-budget/calculate")
def calculate_calorie_budget(req: CalorieBudgetCalculateRequest):
    budget = calculate_daily_calorie_target(
        weight_kg=req.weight_kg,
        height_cm=req.height_cm,
        age=req.age,
        gender=req.gender,
        activity_level=req.activity_level,
        goal=req.goal,
        goal_delta_kcal=req.goal_delta_kcal or 500.0,
    )
    # Default meal slot weights: breakfast 25%, lunch 35%, snack 10%, dinner 30%
    target_cals = budget["target_calories"]
    slot_targets = {
        "breakfast": round(target_cals * 0.25, 1),
        "lunch": round(target_cals * 0.35, 1),
        "snack": round(target_cals * 0.10, 1),
        "dinner": round(target_cals * 0.30, 1),
    }

    return {
        "bmr": budget["bmr"],
        "tdee": budget["tdee"],
        "target_calories": target_cals,
        "slot_targets": slot_targets,
        "sum_slot_targets": round(sum(slot_targets.values()), 1),
    }

