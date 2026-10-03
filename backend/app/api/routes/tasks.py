from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
)


# Temporary development user.
# This will be replaced by real authentication later.
DEVELOPMENT_USER_ID = 1


@router.post("/", response_model=TaskResponse)
def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
):
    task = Task(
        user_id=DEVELOPMENT_USER_ID,
        title=task_data.title,
        description=task_data.description,
        status=task_data.status,
        priority=task_data.priority,
        due_at=task_data.due_at,
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return task


@router.get("/", response_model=list[TaskResponse])
def get_tasks(
    db: Session = Depends(get_db),
):
    return (
        db.query(Task)
        .filter(Task.user_id == DEVELOPMENT_USER_ID)
        .all()
    )


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
):
    task = (
        db.query(Task)
        .filter(
            Task.id == task_id,
            Task.user_id == DEVELOPMENT_USER_ID,
        )
        .first()
    )

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    return task


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
):
    task = (
        db.query(Task)
        .filter(
            Task.id == task_id,
            Task.user_id == DEVELOPMENT_USER_ID,
        )
        .first()
    )

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    update_data = task_data.model_dump(
        exclude_unset=True,
    )

    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)

    return task


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
):
    task = (
        db.query(Task)
        .filter(
            Task.id == task_id,
            Task.user_id == DEVELOPMENT_USER_ID,
        )
        .first()
    )

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    db.delete(task)
    db.commit()

    return {
        "message": "Task deleted successfully",
    }