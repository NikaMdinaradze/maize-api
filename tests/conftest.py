from typing import Any, AsyncGenerator

import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from src.deps import get_db
from src.main import app as _app
from src.settings import engine

AsyncSessionTesting = async_sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession
)


@pytest_asyncio.fixture(scope="function")
async def app() -> AsyncGenerator[FastAPI, Any]:
    """
    Create a fresh database on each test case.
    """
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield _app
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def db_session(app: FastAPI) -> AsyncGenerator[AsyncSession, Any]:
    async with AsyncSessionTesting() as session:
        yield session  # use the session in tests


@pytest_asyncio.fixture(scope="function")
async def client(
    app: FastAPI, db_session: AsyncSession
) -> AsyncGenerator[AsyncClient, Any]:
    """
    Create a new FastAPI AsyncClient that uses the `db_session` fixture to override
    the `get_db` dependency that is injected into routes.
    """

    async def _get_test_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _get_test_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://127.0.0.1"
    ) as client:
        yield client
