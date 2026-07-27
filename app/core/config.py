from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "SecureTaskAPI"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    # Security
    SECRET_KEY: str = Field(..., description="JWT secret key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database
    DATABASE_URL: str = Field(..., description="Database connection string")

    # Pydantic v2 configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="SECURETASK_",
        case_sensitive=True,
        extra="ignore"
    )

    @property
    def sqlalchemy_database_url(self) -> str:
        """Return a PostgreSQL URL that explicitly uses the installed psycopg 3 driver."""
        if self.DATABASE_URL.startswith("postgres://"):
            return self.DATABASE_URL.replace(
                "postgres://", "postgresql+psycopg://", 1
            )
        if self.DATABASE_URL.startswith("postgresql://"):
            return self.DATABASE_URL.replace(
                "postgresql://", "postgresql+psycopg://", 1
            )
        return self.DATABASE_URL


settings = Settings()
