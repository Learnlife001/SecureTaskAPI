import secrets

from fastapi import FastAPI, Header, HTTPException, status
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
def metrics(x_metrics_token: str | None = Header(default=None)):
    if not settings.METRICS_TOKEN:
        if settings.ENVIRONMENT == "production":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Metrics access is not configured",
            )
    elif not x_metrics_token or not secrets.compare_digest(
        x_metrics_token, settings.METRICS_TOKEN
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid metrics token",
        )
    return metrics_response()
