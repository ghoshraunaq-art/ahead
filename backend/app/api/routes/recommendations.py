from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.recommendation import RecommendationResponse
from app.services.recommendations import generate_recommendations


router = APIRouter(
    prefix="/intelligence",
    tags=["intelligence"],
)

# Temporary development identity, consistent with existing endpoints.
DEVELOPMENT_USER_ID = 1


@router.get(
    "/recommendations",
    response_model=RecommendationResponse,
)
def get_recommendations(
    db: Session = Depends(get_db),
) -> RecommendationResponse:
    try:
        return generate_recommendations(
            db=db,
            user_id=DEVELOPMENT_USER_ID,
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=404,
            detail="Development user not found",
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc