from fastapi import FastAPI

app = FastAPI(title="Ahead API")


@app.get("/")
def read_root():
    return {
        "message": "Welcome to Ahead",
        "status": "backend is running"
    }