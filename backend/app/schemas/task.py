from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


TaskStatus = Literal[
    "pending",
    "in_progress",
    "completed",
    "cancelled",
]

TaskPriority = Literal[
    "low",
    "normal",
    "high",
]


class TaskCreate(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=200,
    )
    description: str | None = None
    status: TaskStatus = "pending"
    priority: TaskPriority = "normal"
    due_at: datetime | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Title cannot be empty")

        return value


class TaskUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    due_at: datetime | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()

        if not value:
            raise ValueError("Title cannot be empty")

        return value


class TaskResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: str | None
    status: str
    priority: str
    due_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)