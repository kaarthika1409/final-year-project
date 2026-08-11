import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import User, DailyTarget, MealLog
from backend.app.schemas import DailyTargetResponse, MealSlotBreakdown
from backend.app.security import get_current_user
from backend.app.budget_engine import calculate_daily_calorie_target
from backend.app.redistribution import recalculate_and_redistribute_daily_target

router = APIRouter(prefix="/api/targets", tags=["Calorie Targets & Adaptive Redistribution"])


def get_or_create_daily_target(user: User, db: Session, target_date: str = None) -> DailyTarget:
    if target_date is None:
        target_date = datetime.date.today().isoformat()

    daily_target = (
        db.query(DailyTarget)
        .filter(DailyTarget.user_id == user.id, DailyTarget.date == target_date)
        .first()
    )

    budget = calculate_daily_calorie_target(
        user.weight, user.height, user.age, user.gender, user.activity_level, user.goal
    )

    if not daily_target:
        daily_target = DailyTarget(
            user_id=user.id,
            date=target_date,
            bmr=budget["bmr"],
            target_calories=budget["target_calories"],
            consumed_calories=0.0,
            remaining_calories=budget["target_calories"],
            target_protein=budget["target_protein"],
            target_carbs=budget["target_carbs"],
            target_fat=budget["target_fat"],
            consumed_protein=0.0,
            consumed_carbs=0.0,
            consumed_fat=0.0,
            breakfast_target=round(budget["target_calories"] * 0.25, 1),
            lunch_target=round(budget["target_calories"] * 0.35, 1),
            snacks_target=round(budget["target_calories"] * 0.15, 1),
            dinner_target=round(budget["target_calories"] * 0.25, 1),
            breakfast_consumed=0.0,
            lunch_consumed=0.0,
            snacks_consumed=0.0,
            dinner_consumed=0.0,
        )
        db.add(daily_target)
        db.commit()
        db.refresh(daily_target)
    else:
        # Update target calories if user changed profile parameters
        if daily_target.target_calories != budget["target_calories"]:
            daily_target.bmr = budget["bmr"]
            daily_target.target_calories = budget["target_calories"]
            daily_target.target_protein = budget["target_protein"]
            daily_target.target_carbs = budget["target_carbs"]
            daily_target.target_fat = budget["target_fat"]

    # Fetch today's meal logs for recalculation
    logs = (
        db.query(MealLog)
        .filter(
            MealLog.user_id == user.id,
            MealLog.timestamp >= datetime.datetime.strptime(target_date, "%Y-%m-%d"),
            MealLog.timestamp < datetime.datetime.strptime(target_date, "%Y-%m-%d") + datetime.timedelta(days=1),
        )
        .all()
    )

    daily_target = recalculate_and_redistribute_daily_target(daily_target, logs)
    db.commit()
    db.refresh(daily_target)
    return daily_target


def format_target_response(target: DailyTarget) -> DailyTargetResponse:
    remaining_p = max(0.0, round(target.target_protein - target.consumed_protein, 1))
    remaining_c = max(0.0, round(target.target_carbs - target.consumed_carbs, 1))
    remaining_f = max(0.0, round(target.target_fat - target.consumed_fat, 1))

    return DailyTargetResponse(
        id=target.id,
        user_id=target.user_id,
        date=target.date,
        bmr=target.bmr,
        target_calories=target.target_calories,
        consumed_calories=target.consumed_calories,
        remaining_calories=target.remaining_calories,
        target_protein=target.target_protein,
        target_carbs=target.target_carbs,
        target_fat=target.target_fat,
        consumed_protein=target.consumed_protein,
        consumed_carbs=target.consumed_carbs,
        consumed_fat=target.consumed_fat,
        remaining_protein=remaining_p,
        remaining_carbs=remaining_c,
        remaining_fat=remaining_f,
        breakfast=MealSlotBreakdown(
            target=target.breakfast_target,
            consumed=target.breakfast_consumed,
            remaining=max(0.0, round(target.breakfast_target - target.breakfast_consumed, 1)),
        ),
        lunch=MealSlotBreakdown(
            target=target.lunch_target,
            consumed=target.lunch_consumed,
            remaining=max(0.0, round(target.lunch_target - target.lunch_consumed, 1)),
        ),
        snacks=MealSlotBreakdown(
            target=target.snacks_target,
            consumed=target.snacks_consumed,
            remaining=max(0.0, round(target.snacks_target - target.snacks_consumed, 1)),
        ),
        dinner=MealSlotBreakdown(
            target=target.dinner_target,
            consumed=target.dinner_consumed,
            remaining=max(0.0, round(target.dinner_target - target.dinner_consumed, 1)),
        ),
    )


@router.get("/today", response_model=DailyTargetResponse)
def get_today_target(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    target = get_or_create_daily_target(current_user, db)
    return format_target_response(target)


@router.post("/recalculate", response_model=DailyTargetResponse)
def force_recalculate_target(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    target = get_or_create_daily_target(current_user, db)
    return format_target_response(target)
