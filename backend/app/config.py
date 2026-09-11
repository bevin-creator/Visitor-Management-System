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

    #CORS for frontend origin
    CORS_ORIGINS:list[str]= ["http://localhost:5500", "http://127.0.0.1:5500"]
    
    ENCRYPTION_KEY: str = "generate-key"

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

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def split_cors(cls, v):
        # Allow a comma-separated string from an env var
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    class Config:
        env_file=".env"

settings=Settings()