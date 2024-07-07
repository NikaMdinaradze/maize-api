from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.models.token import TokenPayload
from src.models.user import User
from src.settings import async_session, settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_db() -> AsyncSession:
    """
    Get a database session.

    Yields:
        AsyncSession: An asynchronous SQLAlchemy session.
    """
    async with async_session() as session:
        yield session


def verify_token(token: Annotated[str, Depends(oauth2_scheme)]) -> TokenPayload:
    """
    Verify and decode a JWT token.

    Args:
        token (str): JWT token obtained from the login (OAuth2 scheme).

    Returns:
        TokenPayload: The payload data of the token.

    Raises:
        HTTPException: If the token is invalid, cannot be decoded or expired.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    return token_data


def verify_access_token(token_data: TokenPayload = Depends(verify_token)) -> TokenPayload:
    """
    Verify that the token is an access token.

    Args:
        token_data (TokenPayload): The payload data of the token.

    Returns:
        TokenPayload: The payload data if it is an access token.

    Raises:
        HTTPException: If the token is not an access token.
    """
    if token_data.token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials. Expected access token.",
        )
    return token_data


def verify_refresh_token(
    token_data: TokenPayload = Depends(verify_token),
) -> TokenPayload:
    """
    Verify that the token is a refresh token.

    Args:
        token_data (TokenPayload): The payload data of the token.

    Returns:
        TokenPayload: The payload data if it is a refresh token.

    Raises:
        HTTPException: If the token is not a refresh token.
    """
    if token_data.token_type != "refresh":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials. Expected refresh token.",
        )
    return token_data


def verify_one_time_token(
    token_data: TokenPayload = Depends(verify_token),
) -> TokenPayload:
    """

    Verify that the token is a one-time token.

    Args:
        token_data (TokenPayload): The payload data of the token.

    Returns:
        TokenPayload: The payload data of the token if it is a one-time token.

    Raises:
        HTTPException: If the token is invalid or not a one-time token.
    """
    if token_data.token_type != "one-time":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials. Expected one time token.",
        )
    return token_data


async def get_current_user(
    token_data: TokenPayload = Depends(verify_access_token),
    session: AsyncSession = Depends(get_db),
) -> User:
    """
    Get the current user from the database.

    Args:
        token_data (TokenPayload): The payload data of the token.
        session (AsyncSession): The database session.

    Returns:
        User: The current user.

    Raises:
        HTTPException: If the user is not found.
    """
    statement = select(User).where(User.id == token_data.user_id)
    result = await session.exec(statement)
    user = result.first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get the current active user.

    Args:
        current_user (User): The current user.

    Returns:
        User: The current active (verified) user.

    Raises:
        HTTPException: If the user is inactive.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
