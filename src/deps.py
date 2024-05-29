from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import sessionmaker
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.models.token import TokenPayload
from src.models.user import User
from src.settings import ALGORITHM, SECRET_KEY, engine

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_db() -> AsyncSession:
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


def verify_token(token: Annotated[str, Depends(oauth2_scheme)]) -> TokenPayload:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_data = TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    return token_data


def verify_access_token(token_data: TokenPayload = Depends(verify_token)) -> TokenPayload:
    if token_data.token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials. Expected access token.",
        )
    return token_data


def verify_refresh_token(
    token_data: TokenPayload = Depends(verify_token),
) -> TokenPayload:
    if token_data.token_type != "refresh":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials. Expected refresh token.",
        )
    return token_data


def verify_one_time_token(token: str) -> TokenPayload:
    """
    TODO: should be in header when front is added
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_data = TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
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
    statement = select(User).where(User.id == token_data.user_id)
    result = await session.exec(statement)
    user = result.first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
