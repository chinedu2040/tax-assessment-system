import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://taxuser:taxpass@db:5432/taxdb"
    upload_dir: str = "/app/uploads"
    report_dir: str = "/app/reports"
    secret_key: str = "change-this-in-production"
    env: str = "development"
    frontend_url: str = "http://localhost:3000"
    max_upload_size_mb: int = 10

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
