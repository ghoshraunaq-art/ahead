from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


RecommendationPriority = Literal["high", "normal", "low"]


class Recommendation(BaseModel):
    code: str
    title: str
    message: str
    priority: RecommendationPriority
    entity_type: Literal["task", "event"]
    entity_id: int
    context_ids: list[int] = Field(default_factory=list)


class RecommendationResponse(BaseModel):
    generated_at: datetime
    timezone: str
    recommendations: list[Recommendation]

    model_config = ConfigDict(from_attributes=True)