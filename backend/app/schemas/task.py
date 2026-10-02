from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    status: str = "pending"
    priority: str = "normal"
    due_at: datetime | None = None


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