"""
This module provides configuration settings and utilities for the application.
"""
import os
from datetime import timedelta

from mako.lookup import TemplateLookup
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

# database config
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", 5432)
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
TEST_DB_NAME = "test_" + DB_NAME


def get_postgres_url(
    host: str = DB_HOST,
    port: str = DB_PORT,
    db_name: str = DB_NAME,
    user: str = DB_USER,
    password: str = DB_PASSWORD,
) -> str:
    """
    Construct a PostgreSQL URL based on provided or default values.
    """
    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db_name}"


POSTGRES_URL = get_postgres_url()
engine = create_async_engine(POSTGRES_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# security config
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRATION = timedelta(minutes=5)
REFRESH_TOKEN_EXPIRATION = timedelta(days=7)
ONE_TIME_TOKEN_EXPIRATION = timedelta(minutes=3)
FRONTEND_URL = os.getenv("FRONTEND_URL")
pwd_cxt = CryptContext(schemes=["bcrypt"], deprecated="auto")

# email config
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# html
lookup = TemplateLookup(directories=["src/templates"])
