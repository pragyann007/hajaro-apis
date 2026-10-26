from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# app/core/config.py -> app/ -> project root (where .env lives)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"

class Settings(BaseSettings):
    PROJECT_NAME: str = "Hajaro Backend Infrastructure"
    API_V1_PREFIX: str = "/hajaro/api/v1"
    DATABASE_URL: str
    ACCESS_TOKEN_TTL_MINUTES: int
    ACCESS_TOKEN_SECRET_KEY: str
    REFRESH_TOKEN_TTL_MINUTES: int
    REFRESH_TOKEN_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ENVIRONMENT: str = "development"

    # Configuration for pydantic-settings to read from the root .env file
    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()