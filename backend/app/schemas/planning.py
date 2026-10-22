from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class PlanningContextItem(BaseModel):
    id: int
    context_type: str
    title: str
    value: str
    source: str
    extra_data: dict[str, Any] | None = None


class PlannedTask(BaseModel):
    id: int
    title: str
    description: str | None
    status: str
    priority: str
    due_at: datetime | None
    context: list[PlanningContextItem] = []


class PlannedEvent(BaseModel):
    id: int
    title: str
    description: str | None
    starts_at: datetime
    ends_at: datetime | None
    context: list[PlanningContextItem] = []


class PlannedReminder(BaseModel):
    id: int
    title: str
    message: str | None
    remind_at: datetime
    status: str
    context: list[PlanningContextItem] = []


class PlanningObservation(BaseModel):
    code: str
    message: str
    entity_type: str
    entity_id: int


class DailyPlanningResponse(BaseModel):
    plan_date: date
    timezone: str
    tasks: list[PlannedTask]
    events: list[PlannedEvent]
    reminders: list[PlannedReminder]
    observations: list[PlanningObservation]

    model_config = ConfigDict(from_attributes=True)