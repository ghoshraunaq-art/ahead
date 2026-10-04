from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class EventCreate(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=200,
    )
    description: str | None = None
    starts_at: datetime
    ends_at: datetime | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Title cannot be empty")

        return value

    @field_validator("starts_at", "ends_at")
    @classmethod
    def validate_timezone(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return None

        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Datetime must include timezone information")

        return value

    @model_validator(mode="after")
    def validate_event_times(self):
        if self.ends_at is not None and self.ends_at <= self.starts_at:
            raise ValueError("ends_at must be later than starts_at")

        return self


class EventUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )
    description: str | None = None
    starts_at: datetime | None = None
    ends_at: datetime | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()

        if not value:
            raise ValueError("Title cannot be empty")

        return value

    @field_validator("starts_at", "ends_at")
    @classmethod
    def validate_timezone(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return None

        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Datetime must include timezone information")

        return value


class EventResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: str | None
    starts_at: datetime
    ends_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)