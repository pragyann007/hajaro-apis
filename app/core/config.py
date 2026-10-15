from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Hajaro Backend Infrastructure"
    API_V1_PREFIX: str = "/hajaro/api/v1"
    DATABASE_URL: str

    # Configuration for pydantic-settings to read from the root .env file
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()