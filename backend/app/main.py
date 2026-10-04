from fastapi import FastAPI

from app.api.routes.events import router as events_router
from app.api.routes.health import router as health_router
from app.api.routes.reminders import router as reminders_router
from app.api.routes.tasks import router as tasks_router
from app.core.config import settings

app = FastAPI(title=settings.app_name)

app.include_router(health_router)
app.include_router(tasks_router)
app.include_router(events_router)
app.include_router(reminders_router)


@app.get("/")
def read_root():
    return {
        "message": "Welcome to Ahead",
        "status": "backend is running",
        "environment": settings.environment,
    }