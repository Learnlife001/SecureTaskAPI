from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool
from app.core.config import settings

engine_options = {"echo": settings.DEBUG, "pool_pre_ping": True}

# A single in-memory SQLite connection is required for the test client. Other
# database URLs (including PostgreSQL in Docker) keep SQLAlchemy's defaults.
if settings.sqlalchemy_database_url.startswith("sqlite"):
    engine_options.update(
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    engine_options.update(
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
    )

engine = create_engine(settings.sqlalchemy_database_url, **engine_options)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
