import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/dbname"
    GOOGLE_CREDENTIALS_FILE: str = "credentials.json"
    GOOGLE_SHEET_ID: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
