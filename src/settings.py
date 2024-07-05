"""
This module provides configuration settings and utilities for the application.
"""
from datetime import timedelta

from mako.lookup import TemplateLookup
from passlib.context import CryptContext
from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession


class Settings(BaseSettings):
    """
    Application settings class defining configuration parameters from environment.
    """

    DB_HOST: str
    DB_PORT: int = 5432
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRATION: timedelta = timedelta(minutes=5)
    REFRESH_TOKEN_EXPIRATION: timedelta = timedelta(days=7)
    ONE_TIME_TOKEN_EXPIRATION: timedelta = timedelta(minutes=3)
    FRONTEND_URL: str | None = "http://127.0.0.1:3000"

    EMAIL_SENDER: str | None = None
    EMAIL_PASSWORD: str | None = None

    @property
    def postgres_url(self) -> PostgresDsn:
        """
        Computed property returning the PostgreSQL connection URL.
        """
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


class TestSettings(Settings):
    """
    Test settings class extending base application settings. Use for pytest.
    """

    @field_validator("DB_NAME")
    def add_test_prefix(cls, name: str) -> str:
        return "test_" + name


settings = Settings()
test_settings = TestSettings()

engine = create_async_engine(settings.postgres_url, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

pwd_cxt = CryptContext(schemes=["bcrypt"], deprecated="auto")

# html
lookup = TemplateLookup(directories=["src/templates"])
