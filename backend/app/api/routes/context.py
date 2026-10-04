from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.models.context import ContextItem
from app.schemas.context import ContextCreate, ContextResponse, ContextUpdate

router = APIRouter(
    prefix="/context",
    tags=["context"],
)


# Temporary development user.
# This will be replaced by real authentication later.
DEVELOPMENT_USER_ID = 1


@router.post("/", response_model=ContextResponse)
def create_context(
    context_data: ContextCreate,
    db: Session = Depends(get_db),
):
    context_item = ContextItem(
        user_id=DEVELOPMENT_USER_ID,
        context_type=context_data.context_type,
        title=context_data.title,
        value=context_data.value,
        source=context_data.source,
        extra_data=context_data.extra_data,
    )

    db.add(context_item)
    db.commit()
    db.refresh(context_item)

    return context_item


@router.get("/", response_model=list[ContextResponse])
def get_context(
    db: Session = Depends(get_db),
):
    return (
        db.query(ContextItem)
        .filter(ContextItem.user_id == DEVELOPMENT_USER_ID)
        .order_by(ContextItem.created_at.desc())
        .all()
    )


@router.get("/{context_id}", response_model=ContextResponse)
def get_context_item(
    context_id: int,
    db: Session = Depends(get_db),
):
    context_item = (
        db.query(ContextItem)
        .filter(
            ContextItem.id == context_id,
            ContextItem.user_id == DEVELOPMENT_USER_ID,
        )
        .first()
    )

    if context_item is None:
        raise HTTPException(
            status_code=404,
            detail="Context item not found",
        )

    return context_item


@router.patch("/{context_id}", response_model=ContextResponse)
def update_context(
    context_id: int,
    context_data: ContextUpdate,
    db: Session = Depends(get_db),
):
    context_item = (
        db.query(ContextItem)
        .filter(
            ContextItem.id == context_id,
            ContextItem.user_id == DEVELOPMENT_USER_ID,
        )
        .first()
    )

    if context_item is None:
        raise HTTPException(
            status_code=404,
            detail="Context item not found",
        )

    update_data = context_data.model_dump(
        exclude_unset=True,
    )

    for field, value in update_data.items():
        setattr(context_item, field, value)

    db.commit()
    db.refresh(context_item)

    return context_item


@router.delete("/{context_id}")
def delete_context(
    context_id: int,
    db: Session = Depends(get_db),
):
    context_item = (
        db.query(ContextItem)
        .filter(
            ContextItem.id == context_id,
            ContextItem.user_id == DEVELOPMENT_USER_ID,
        )
        .first()
    )

    if context_item is None:
        raise HTTPException(
            status_code=404,
            detail="Context item not found",
        )

    db.delete(context_item)
    db.commit()

    return {
        "message": "Context item deleted successfully",
    }