from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


ContextType = Literal[
    "fact",
    "preference",
    "constraint",
    "routine",
]

ContextSource = Literal[
    "manual",
    "ai",
    "import",
]


class ContextCreate(BaseModel):
    context_type: ContextType
    title: str = Field(
        min_length=1,
        max_length=200,
    )
    value: str = Field(
        min_length=1,
    )
    source: ContextSource = "manual"
    extra_data: dict | None = None

    @field_validator("title", "value")
    @classmethod
    def validate_text(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Value cannot be empty")

        return value


class ContextUpdate(BaseModel):
    context_type: ContextType | None = None
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )
    value: str | None = Field(
        default=None,
        min_length=1,
    )
    source: ContextSource | None = None
    extra_data: dict | None = None

    @field_validator("title", "value")
    @classmethod
    def validate_text(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()

        if not value:
            raise ValueError("Value cannot be empty")

        return value


class ContextResponse(BaseModel):
    id: int
    user_id: int
    context_type: str
    title: str
    value: str
    source: str
    extra_data: dict | None
    created_at: object
    updated_at: object

    model_config = ConfigDict(from_attributes=True)