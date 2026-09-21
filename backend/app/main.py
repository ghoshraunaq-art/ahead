from fastapi import FastAPI

from app.api.routes.health import router as health_router

app = FastAPI(title="Ahead API")

app.include_router(health_router)


@app.get("/")
def read_root():
    return {
        "message": "Welcome to Ahead",
        "status": "backend is running"
    }