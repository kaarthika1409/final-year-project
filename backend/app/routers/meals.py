import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import User, MealLog, NutritionReference
from backend.app.schemas import (
    MealLogCreate,
    MealLogResponse,
    PhotoDetectResponse,
    DailyTargetResponse,
)
from backend.app.security import get_current_user
from backend.app.ml_service import predict_food_from_image, fuzzy_match_nutrition_db
from backend.app.routers.targets import get_or_create_daily_target, format_target_response

router = APIRouter(prefix="/api/meals", tags=["Meal Logging"])


@router.get("/search")
def search_nutrition_database(q: str, db: Session = Depends(get_db)):
    if not q or len(q.strip()) == 0:
        return db.query(NutritionReference).limit(20).all()

    term = f"%{q.strip()}%"
    results = (
        db.query(NutritionReference)
        .filter(NutritionReference.food_name.ilike(term) | NutritionReference.category.ilike(term))
        .limit(20)
        .all()
    )

    if not results:
        # Fallback to fuzzy match if exact substring has no results
        dummy_match, matched_name, score = fuzzy_match_nutrition_db(q, db)
        if dummy_match and score >= 50.0:
            results = [dummy_match]

    return results


@router.post("/manual", response_model=dict)
def log_meal_manual(
    meal_in: MealLogCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    # Lookup food in reference table
    db_item, matched_name, score = fuzzy_match_nutrition_db(meal_in.food_name, db)

    portion_factor = meal_in.quantity_g / 100.0

    if db_item and score >= 45.0:
        calories = round(db_item.calories * portion_factor, 1)
        protein = round(db_item.protein * portion_factor, 1)
        carbs = round(db_item.carbs * portion_factor, 1)
        fat = round(db_item.fat * portion_factor, 1)
        food_name = db_item.food_name
    else:
        # Generic macro estimate if user inputs custom name not in DB
        calories = round(200.0 * portion_factor, 1)
        protein = round(10.0 * portion_factor, 1)
        carbs = round(25.0 * portion_factor, 1)
        fat = round(7.0 * portion_factor, 1)
        food_name = meal_in.food_name

    new_log = MealLog(
        user_id=current_user.id,
        timestamp=datetime.datetime.utcnow(),
        meal_slot=meal_in.meal_slot.lower(),
        food_name=food_name,
        calories=calories,
        protein=protein,
        carbs=carbs,
        fat=fat,
        quantity_g=meal_in.quantity_g,
        source=meal_in.source,
        image_url=meal_in.image_url,
    )
    db.add(new_log)
    db.commit()
    db.refresh(new_log)

    # Recalculate daily target & redistribution
    target = get_or_create_daily_target(current_user, db)

    return {
        "message": "Meal logged successfully",
        "meal_log": MealLogResponse.model_validate(new_log),
        "updated_target": format_target_response(target),
    }


@router.post("/photo", response_model=PhotoDetectResponse)
async def detect_food_from_photo(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must be an image (JPEG, PNG, WebP)",
        )

    contents = await file.read()
    detection = predict_food_from_image(contents, db)

    return PhotoDetectResponse(
        detected_food=detection["detected_food"],
        confidence=detection["confidence"],
        portion_g=detection["portion_g"],
        calories=detection["calories"],
        protein=detection["protein"],
        carbs=detection["carbs"],
        fat=detection["fat"],
        match_source=detection["match_source"],
    )


@router.get("/logs", response_model=List[MealLogResponse])
def get_today_meal_logs(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    today_start = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
    today_end = datetime.datetime.combine(datetime.date.today(), datetime.time.max)

    logs = (
        db.query(MealLog)
        .filter(
            MealLog.user_id == current_user.id,
            MealLog.timestamp >= today_start,
            MealLog.timestamp <= today_end,
        )
        .order_by(MealLog.timestamp.desc())
        .all()
    )

    return [MealLogResponse.model_validate(l) for l in logs]


@router.delete("/logs/{log_id}", response_model=dict)
def delete_meal_log(
    log_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    log = db.query(MealLog).filter(MealLog.id == log_id, MealLog.user_id == current_user.id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Meal log not found")

    db.delete(log)
    db.commit()

    target = get_or_create_daily_target(current_user, db)

    return {
        "message": "Meal log deleted",
        "updated_target": format_target_response(target),
    }
