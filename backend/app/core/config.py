from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True, extra="ignore")

    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@db:5432/app"
    BACKEND_CORS_ORIGINS: str = "http://localhost:5173"


settings = Settings()
