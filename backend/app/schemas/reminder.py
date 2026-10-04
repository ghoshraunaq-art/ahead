from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


ReminderStatus = Literal[
    "pending",
    "triggered",
    "cancelled",
]


class ReminderCreate(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=200,
    )
    message: str | None = None
    remind_at: datetime
    status: ReminderStatus = "pending"

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Title cannot be empty")

        return value

    @field_validator("remind_at")
    @classmethod
    def validate_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Datetime must include timezone information")

        return value


class ReminderUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )
    message: str | None = None
    remind_at: datetime | None = None
    status: ReminderStatus | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()

        if not value:
            raise ValueError("Title cannot be empty")

        return value

    @field_validator("remind_at")
    @classmethod
    def validate_timezone(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return None

        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Datetime must include timezone information")

        return value


class ReminderResponse(BaseModel):
    id: int
    user_id: int
    title: str
    message: str | None
    remind_at: datetime
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)