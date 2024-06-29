from datetime import timedelta
from unittest.mock import AsyncMock, patch

from httpx import AsyncClient
from jose import jwt
from sqlmodel.ext.asyncio.session import AsyncSession

from src.endpoints.auth import success_html
from src.JWT import JWTToken
from src.models.token import TokenPayload
from src.settings import ALGORITHM, SECRET_KEY, pwd_cxt
from tests.utils import create_user


async def test_register(client: AsyncClient) -> None:
    """
    Test the registration of a new user.

    This test checks if a new user can be registered successfully.
    It verifies that the response contains the correct user details and
    that the account is initially inactive.
    """
    payload = {"email": "activeuser@example.com", "password": "String123"}

    with patch("src.tasks.send_mail", new_callable=AsyncMock):
        response = await client.post("/auth/register", json=payload)
        response_data = response.json()
        assert response.status_code == 200
        assert response_data["email"] == payload["email"]
        assert "id" in response_data
        assert response_data["role"] == "customer"
        assert response_data["is_active"] is False


async def test_register_invalid_passwords(client: AsyncClient) -> None:
    """
    Test the registration of a new user with invalid password.
    """
    invalid_passwords = (
        "",
        "abc",
        "ab1",
        "12345678",
        "A1234",
        "Abc12345678901234fbgfdestyhnmffksjndmnfsdf",
    )
    email = "user@example.com"
    for password in invalid_passwords:
        payload = {"email": email, "password": password}
        response = await client.post("/auth/register", json=payload)
        assert response.status_code == 422


async def test_register_existing_active_user(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """
    Test registration with an already active user.

    This test checks if the registration process correctly handles the case where
    an active user with the same email already exists. It verifies that an appropriate
    error message is returned.
    """
    payload = {"email": "activeuser@example.com", "password": "String123"}
    await create_user(db_session, payload["email"], payload["password"], is_active=True)

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
    payload = {"email": "inactiveuser@example.com", "password": "String123"}

    await create_user(db_session, payload["email"], payload["password"])

    with patch("src.tasks.send_mail", new_callable=AsyncMock):
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

    Note that username is used instead of email because of OAuth2PasswordRequestForm.
    """
    payload = {"username": "existinguser@example.com", "password": "String123"}

    db_user = await create_user(
        db_session, payload["username"], payload["password"], is_active=True
    )
    response = await client.post(
        "/auth/login",
        data={"username": payload["username"], "password": payload["password"]},
    )
    assert response.status_code == 200
    response_data = response.json()

    access_token_payload = jwt.decode(
        response_data["access_token"], SECRET_KEY, algorithms=[ALGORITHM]
    )
    refresh_token_payload = jwt.decode(
        response_data["refresh_token"], SECRET_KEY, algorithms=[ALGORITHM]
    )

    assert access_token_payload["user_id"] == str(db_user.id)
    assert refresh_token_payload["user_id"] == str(db_user.id)
    assert response_data["user_id"] == str(db_user.id)
    assert response_data["token_type"] == "bearer"


async def test_login_non_existent_user(client: AsyncClient) -> None:
    """
    Test login with non-existent user.

    This test checks if the login process correctly handles the case where
    the user does not exist. It verifies that an appropriate error message
    is returned.

    Note that username is used instead of email because of OAuth2PasswordRequestForm.
    """
    payload = {"username": "nonexistent@example.com", "password": "String123"}

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

    Note that username is used instead of email because of OAuth2PasswordRequestForm.
    """
    payload = {"username": "existinguser@example.com", "password": "wrongpassword"}

    await create_user(db_session, payload["username"], "password123", is_active=True)

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

    Note that username is used instead of email because of OAuth2PasswordRequestForm.
    """
    payload = {"username": "inactiveuser@example.com", "password": "password123"}

    await create_user(db_session, payload["username"], payload["password"])

    response = await client.post(
        "/auth/login",
        data={"username": payload["username"], "password": payload["password"]},
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Activate Account"}


async def test_refresh_access_token(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """
    Test refreshing the access token using a valid refresh token.

    This test checks if a user can get a new access token using a valid refresh token.
    """
    payload = {"email": "existinguser@example.com", "password": "password123"}

    db_user = await create_user(
        db_session, payload["email"], payload["password"], is_active=True
    )

    refresh_token = JWTToken(db_user.id).get_refresh_token()

    response = await client.post(
        "/auth/refresh",
        headers={"Authorization": f"Bearer {refresh_token}"},
    )

    assert response.status_code == 200
    response_data = response.json()

    access_token_payload = jwt.decode(
        response_data["access_token"], SECRET_KEY, algorithms=[ALGORITHM]
    )
    access_token_data = TokenPayload(**access_token_payload)

    assert access_token_data.user_id == db_user.id
    assert access_token_data.token_type == "access"


async def test_refresh_access_expired_token(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """
    Test refreshing the access token using an invalid expired refresh token.
    """
    payload = {"email": "existinguser@example.com", "password": "password123"}

    db_user = await create_user(
        db_session, payload["email"], payload["password"], is_active=True
    )

    refresh_token = JWTToken(db_user.id).get_refresh_token(
        expires_delta=timedelta(seconds=-1)
    )

    response = await client.post(
        "/auth/refresh",
        headers={"Authorization": f"Bearer {refresh_token}"},
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "Could not validate credentials"}


async def test_verify_email_success(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """
    Test the successful verification of a user's email.
    """
    payload = {"email": "newuser@example.com", "password": "password123"}

    db_user = await create_user(
        db_session, payload["email"], payload["password"], is_active=True
    )

    one_time_token = JWTToken(db_user.id).get_one_time_token()

    response = await client.get("/auth/verify-email", params={"token": one_time_token})
    await db_session.refresh(db_user)

    assert response.status_code == 200
    assert response.text == success_html
    assert db_user.is_active


async def test_verify_expired_email_success(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """
    Test the expired verification of a user's email.
    """
    payload = {"email": "newuser@example.com", "password": "password123"}

    db_user = await create_user(
        db_session, payload["email"], payload["password"], is_active=True
    )
    one_time_token = JWTToken(db_user.id).get_one_time_token(
        expires_delta=timedelta(seconds=-1)
    )

    response = await client.get("/auth/verify-email", params={"token": one_time_token})
    await db_session.refresh(db_user)

    assert response.status_code == 403
    assert response.json() == {"detail": "Could not validate credentials"}


async def test_change_password_success(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """
    Test successful password change for an authenticated user.
    """
    user = await create_user(
        db_session, "user@example.com", "Oldpassword123", is_active=True
    )
    access_token = JWTToken(user.id).get_access_token()

    new_password = "newpassword"
    old_password = "Oldpassword123"

    response = await client.post(
        "/auth/change-password",
        json={"new_password": new_password, "old_password": old_password},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Password updated successfully"}

    # Verify that the password has actually been changed in the database
    await db_session.refresh(user)
    assert pwd_cxt.verify(new_password, user.password)
