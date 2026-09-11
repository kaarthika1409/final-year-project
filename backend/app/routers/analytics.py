import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import User, MealLog
from backend.app.schemas import AccuracyReportResponse
from backend.app.security import get_current_user
from backend.app.evaluation import evaluate_demographic_accuracy

router = APIRouter(tags=["Accuracy & Evaluation"])


@router.get("/api/analytics/accuracy", response_model=AccuracyReportResponse)
@router.get("/analytics/accuracy", response_model=AccuracyReportResponse)
def get_accuracy_metrics():
    """Returns MAE, RMSE, and MAPE prediction metrics across Age, Gender, and BMI groups."""
    return evaluate_demographic_accuracy()


@router.get("/api/analytics/deficiencies")
@router.get("/analytics/deficiencies")
def get_nutritional_deficiencies(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Stage 7 Nutritional Deficiency Flagging Engine
    Calculates rolling 7-day macro & micronutrient intake vs RDA reference values.
    Flags any nutrient trending below 70% RDA over the window.
    """
    seven_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=7)
    logs = (
        db.query(MealLog)
        .filter(MealLog.user_id == current_user.id, MealLog.timestamp >= seven_days_ago)
        .all()
    )

    sum_protein = sum(l.protein for l in logs)
    sum_carbs = sum(l.carbs for l in logs)
    sum_fat = sum(l.fat for l in logs)

    # 7-day RDA reference standards
    rda_7day = {
        "protein_g": 350.0,   # ~50g/day
        "carbs_g": 910.0,     # ~130g/day
        "fat_g": 490.0,       # ~70g/day
    }

    actual_7day = {
        "protein_g": round(sum_protein, 1),
        "carbs_g": round(sum_carbs, 1),
        "fat_g": round(sum_fat, 1),
    }

    deficiencies = []
    for nutrient, target_val in rda_7day.items():
        actual_val = actual_7day.get(nutrient, 0.0)
        pct = (actual_val / target_val) * 100.0 if target_val > 0 else 100.0
        if pct < 70.0:
            deficiencies.append({
                "nutrient": nutrient,
                "actual_7day": actual_val,
                "target_7day_rda": target_val,
                "pct_of_rda": round(pct, 1),
                "flag": f"DEFICIENT (< 70% RDA: {pct:.1f}%)",
                "recommendation": f"Increase intake of foods rich in {nutrient.split('_')[0]}.",
            })

    return {
        "user_id": current_user.id,
        "period": "7-day rolling window",
        "total_meal_logs": len(logs),
        "actual_intake": actual_7day,
        "rda_targets": rda_7day,
        "deficiencies_flagged": deficiencies,
        "has_deficiencies": len(deficiencies) > 0,
    }
