from unittest.mock import MagicMock, patch

from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession

from src.models.user import User
from src.settings import pwd_cxt


async def test_register(client: AsyncClient) -> None:
    payload = {"email": "user@example.com", "password": "string"}

    with patch("fastapi.BackgroundTasks.add_task", new_callable=MagicMock):
        response = await client.post("/auth/register", json=payload)
        response_data = response.json()
        assert response.status_code == 200
        assert response_data["email"] == payload["email"]
        assert "id" in response_data
        assert response_data["role"] == "customer"
        assert response_data["is_active"] is False


async def test_register_existing_active_user(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    payload = {"email": "activeuser@example.com", "password": "password123"}

    db_user = User(email=payload["email"], password=payload["password"], is_active=True)
    db_session.add(db_user)
    await db_session.commit()

    with patch("fastapi.BackgroundTasks.add_task", new_callable=MagicMock):
        response = await client.post("/auth/register", json=payload)
        assert response.status_code == 400
        assert response.json() == {"detail": "email already exists"}


async def test_register_existing_inactive_user(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    payload = {"email": "inactiveuser@example.com", "password": "password123"}

    db_user = User(email=payload["email"], password=payload["password"], is_active=False)
    db_session.add(db_user)
    await db_session.commit()

    with patch("fastapi.BackgroundTasks.add_task", new_callable=MagicMock):
        response = await client.post("/auth/register", json=payload)
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["email"] == payload["email"]
        assert "id" in response_data
        assert response_data["is_active"] is False


async def test_login_success(client: AsyncClient, db_session: AsyncSession) -> None:
    payload = {"username": "existinguser@example.com", "password": "password123"}

    hashed_password = pwd_cxt.hash(payload["password"])
    db_user = User(email=payload["username"], password=hashed_password, is_active=True)
    db_session.add(db_user)
    await db_session.commit()

    response = await client.post(
        "/auth/login",
        data={"username": payload["username"], "password": payload["password"]},
    )
    assert response.status_code == 200
    response_data = response.json()
    assert "access_token" in response_data
    assert "refresh_token" in response_data
    assert response_data["user_id"] == str(db_user.id)
    assert response_data["token_type"] == "bearer"


async def test_login_non_existent_user(client: AsyncClient) -> None:
    payload = {"username": "nonexistent@example.com", "password": "password123"}

    response = await client.post(
        "/auth/login",
        data={"username": payload["username"], "password": payload["password"]},
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "User Doesn't Exist"}


async def test_login_invalid_credentials(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    payload = {"username": "existinguser@example.com", "password": "wrongpassword"}

    db_user = User(
        email=payload["username"], password=pwd_cxt.hash("password123"), is_active=True
    )
    db_session.add(db_user)
    await db_session.commit()

    response = await client.post(
        "/auth/login",
        data={"username": payload["username"], "password": payload["password"]},
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid Credentials"}


async def test_login_inactive_user(client: AsyncClient, db_session: AsyncSession) -> None:
    payload = {"username": "inactiveuser@example.com", "password": "password123"}

    db_user = User(
        email=payload["username"],
        password=pwd_cxt.hash(payload["password"]),
        is_active=False,
    )
    db_session.add(db_user)
    await db_session.commit()

    response = await client.post(
        "/auth/login",
        data={"username": payload["username"], "password": payload["password"]},
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Activate Account"}
