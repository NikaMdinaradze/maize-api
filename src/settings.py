"""
This module provides configuration settings and utilities for the application.
"""
import os
from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel import SQLModel, create_engine

# database config
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", 5432)
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

POSTGRES_URL = (
    f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:" f"{DB_PORT}/{DB_NAME}"
)
engine = AsyncEngine(create_engine(POSTGRES_URL, echo=True))


async def init_db():
    """
    Initialize the database tables.
    """
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


# security config
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRATION = timedelta(minutes=5)
REFRESH_TOKEN_EXPIRATION = timedelta(days=7)
ONE_TIME_TOKEN_EXPIRATION = timedelta(minutes=3)
BACKEND_URL = os.getenv("BACKEND_URL")

# email config
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
