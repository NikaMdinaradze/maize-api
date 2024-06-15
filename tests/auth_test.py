from unittest.mock import MagicMock, patch

from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession

from src.models.user import User
from src.settings import pwd_cxt


async def test_register(client: AsyncClient) -> None:
    """
    Test the registration of a new user.

    This test checks if a new user can be registered successfully.
    It verifies that the response contains the correct user details and
    that the account is initially inactive.
    """
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
    """
    Test registration with an already active user.

    This test checks if the registration process correctly handles the case where
    an active user with the same email already exists. It verifies that an appropriate
    error message is returned.
    """
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
    """
    Test registration with an existing inactive user.

    This test checks if the registration process can handle the case where
    a user with the same email exists but is inactive. It verifies that the
    registration succeeds and the user details are correctly returned.
    """
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
    """
    Test successful user login.

    This test checks if a user with valid credentials can log in successfully.
    It verifies that the response contains the correct tokens and user ID.
    """
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
    """
    Test login with non-existent user.

    This test checks if the login process correctly handles the case where
    the user does not exist. It verifies that an appropriate error message
    is returned.
    """
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
    """
    Test login with invalid credentials.

    This test checks if the login process correctly handles the case where
    the user provides incorrect credentials. It verifies that an appropriate
    error message is returned.
    """
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
    """
    Test login with inactive user.

    This test checks if the login process correctly handles the case where
    the user account is inactive. It verifies that an appropriate error
    message is returned.
    """
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
