from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import text

from .config import settings
from .database import engine
from .routers import tickets

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="DeskFlow helpdesk ticketing API.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tickets.router)

# exposes GET /metrics in Prometheus format
Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)


@app.get("/health", tags=["system"])
def health():
    return {"status": "ok", "app": settings.app_name, "version": settings.app_version}


@app.get("/ready", tags=["system"])
def ready():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as exc:
        return {"status": "not ready", "detail": str(exc)}


@app.get("/", tags=["system"])
def root():
    return {"message": "DeskFlow API. See /docs for the API documentation."}
