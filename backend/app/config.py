# App configuration using pydatic setting
# Loads values from .env file

from pydantic_settings import BaseSettings
from pydantic import field_validator

class Settings(BaseSettings):
    #App metadata
    APP_NAME: str = "Visitors Management System"
    DEBUG: bool = False

    #Database - SQLAlchemy connection string format
    DATABASE_URL: str ="postgresql://postgres:postgres@localhost:5432/visitor_management"

    #Authentication (JWT)
    SECRET_KEY: str = "enter secure secret key"
    ALGORITHM: str = "HS256" #symmetric
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    #CORS for frontend origin. Stored as a comma-separated string so it can be
    #supplied via a plain env var; use cors_origins_list to get the parsed list.
    CORS_ORIGINS: str = "http://localhost:5500,http://127.0.0.1:5500"

    ENCRYPTION_KEY: str = "generate-key"

    #id verification api (optional), leave blank to keep it off, returns not_configured then
    ID_VERIFICATION_API_URL: str = ""
    ID_VERIFICATION_API_KEY: str = ""
    ID_VERIFICATION_TIMEOUT_SECONDS: float = 10.0

    #first admin bootstrap
    ADMIN_USERNAME: str = ""
    ADMIN_PASSWORD: str = ""
    ADMIN_EMAIL: str = ""
    ADMIN_FULL_NAME: str = "System Admin"

    @field_validator("DATABASE_URL")
    @classmethod
    def normalize_db_url(cls, v: str) -> str:
        # postgres:// to postgresql:// for SQLAlchemy
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql://", 1)
        return v

    @property
    def cors_origins_list(self) -> list[str]:
        # Split the comma-separated CORS_ORIGINS string into a clean list
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    class Config:
        env_file=".env"

settings=Settings()
