from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.planning import DailyPlanningResponse
from app.services.planning import build_daily_plan


router = APIRouter(
    prefix="/planning",
    tags=["planning"],
)

# Temporary development user, consistent with the existing API.
DEVELOPMENT_USER_ID = 1


@router.get(
    "/overview",
    response_model=DailyPlanningResponse,
)
def get_daily_overview(
    plan_date: date | None = Query(
        default=None,
        description="Local planning date in YYYY-MM-DD format. Defaults to the user's current local date.",
    ),
    db: Session = Depends(get_db),
) -> DailyPlanningResponse:
    try:
        return build_daily_plan(
            db=db,
            user_id=DEVELOPMENT_USER_ID,
            plan_date=plan_date,
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