from fastapi import APIRouter
from backend.app.schemas import AccuracyReportResponse
from backend.app.evaluation import evaluate_demographic_accuracy

router = APIRouter(prefix="/api/analytics", tags=["Accuracy & Evaluation"])


@router.get("/accuracy", response_model=AccuracyReportResponse)
def get_accuracy_metrics():
    """Returns MAE and RMSE prediction metrics across Age, Gender, and BMI groups."""
    return evaluate_demographic_accuracy()
