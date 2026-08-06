# App configuration using pydatic setting
# Loads values from .env file

from pydantic_settings import BaseSettings

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

    class Config:
        env_file=".env"

settings=Settings()