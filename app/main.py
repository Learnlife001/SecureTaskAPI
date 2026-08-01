from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import settings
from app.core.logging import configure_logging
from app.core.observability import ObservabilityMiddleware, metrics_response
from app.db.database import engine
from app.routers import auth, tasks

configure_logging()

app = FastAPI(
    title="SecureTask API",
    version=settings.VERSION,
    description="Production-ready task API with JWT authentication, RBAC, audit logging and observability.",
    contact={"name": "SecureTask API Maintainers"},
)

app.add_middleware(ObservabilityMiddleware)
if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(auth.router)
app.include_router(tasks.router)


@app.get("/", tags=["Health"])
def root():
    return {"service": settings.APP_NAME, "version": settings.VERSION}


@app.get("/health/live", tags=["Health"])
def liveness():
    return {"status": "ok"}


@app.get("/health/ready", tags=["Health"])
def readiness():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return {"status": "ready", "database": "available"}


@app.get("/metrics", include_in_schema=False)
def metrics():
    return metrics_response()
