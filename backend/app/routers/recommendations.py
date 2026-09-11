from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import User
from backend.app.schemas import RecommendationResponse
from backend.app.security import get_current_user
from backend.app.routers.targets import get_or_create_daily_target
from backend.app.recommendation import get_dietary_recommendations

router = APIRouter(tags=["Adaptive Recommendations"])


@router.post("/api/recommendations")
@router.get("/api/recommendations", response_model=RecommendationResponse)
@router.get("/recommendations", response_model=RecommendationResponse)
def get_recommendations(
    limit: int = 5,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    target = get_or_create_daily_target(current_user, db)
    return get_dietary_recommendations(current_user, target, db, limit=limit)
