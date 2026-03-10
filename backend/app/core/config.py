from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Base de datos
    DATABASE_URL: str

    # Redis
    REDIS_URL: str

    # Seguridad
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # App
    APP_NAME: str = "TechBot"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]

    # NLP
    NLP_MODEL: str = "distilbert-base-multilingual-cased"
    CONFIDENCE_THRESHOLD: float = 0.75

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
