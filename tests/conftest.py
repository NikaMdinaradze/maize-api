import asyncio
from typing import Any, AsyncGenerator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from src.deps import get_db
from src.main import app as _app
from src.settings import TEST_DB_NAME, get_postgres_url
from tests.utils import create_test_db, delete_test_db

TEST_POSTGRES_URL = get_postgres_url(db_name=TEST_DB_NAME)

test_engine = create_async_engine(TEST_POSTGRES_URL, echo=True)
async_session_testing = async_sessionmaker(
    bind=test_engine, expire_on_commit=False, class_=AsyncSession
)


@pytest.fixture(scope="session", autouse=True)
async def setup_and_teardown_test_database():
    await create_test_db()
    yield
    await test_engine.dispose()
    await delete_test_db()


@pytest.fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def app() -> AsyncGenerator[FastAPI, Any]:
    """
    Create a fresh database on each test case.

    TODO: migrations should be used instead of creating all tables
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield _app
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def db_session(app: FastAPI) -> AsyncGenerator[AsyncSession, Any]:
    async with async_session_testing() as session:
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
