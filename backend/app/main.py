from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.core.config import settings


app = FastAPI(title=settings.app_name)

app.include_router(health_router)


@app.get("/")
def read_root():
    return {
        "message": "Welcome to Ahead",
        "status": "backend is running",
        "environment": settings.environment,
    }
