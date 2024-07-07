from fastapi import APIRouter, BackgroundTasks, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.deps import (
    get_current_active_user,
    get_db,
    verify_one_time_token,
    verify_refresh_token,
)
from src.JWT import JWTToken
from src.models import (
    AccessTokenPayload,
    LoginResponsePayload,
    MessageResponse,
    PasswordChange,
    PasswordReset,
    TokenPayload,
    User,
    UserCreate,
    UserView,
)
from src.settings import pwd_cxt
from src.tasks import send_password_reset_email, send_verification_email

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserView)
async def register(
    user: UserCreate,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db),
):
    """
    Register a new user and send verification url (/verify-email).
    If user already exists with same email raises error that it already exists.

    Returns:
        The details of the registered user.
    """

    statement = select(User).where(User.email == user.email)
    result = await session.exec(statement)
    db_user = result.one_or_none()
    if db_user:
        raise HTTPException(status_code=400, detail="email already exists")

    db_user = User(email=user.email, password=pwd_cxt.hash(user.password))
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    token = JWTToken(db_user.id).get_one_time_token()
    background_tasks.add_task(send_verification_email, db_user.email, token)

    return db_user


@router.get("/resend-verification-email", response_model=MessageResponse)
async def resend_verification_email(
    email: EmailStr,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db),
):
    """
    This endpoint will check if a user with the provided email exists and is not already active.
    If the user exists and is not active, it will send a verification email with a one-time token.
    """
    statement = select(User).where(User.email == email)
    result = await session.exec(statement)
    db_user = result.one_or_none()
    if not db_user:
        raise HTTPException(status_code=404, detail="User with this email does not exist")
    if db_user.is_active:
        raise HTTPException(status_code=400, detail="User is already active")
    token = JWTToken(db_user.id).get_one_time_token()
    background_tasks.add_task(send_verification_email, email, token)
    return {"message": "Verification email sent successfully"}


@router.post("/login", response_model=LoginResponsePayload)
async def login(
    request: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_db),
):
    """
    Authenticate and log in a user use application/x-www-form-urlencoded instead of json.

    Returns:
        The access and refresh tokens along with the token type.
    """
    statement = select(User).where(User.email == request.username)
    result = await session.exec(statement)
    user = result.first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User Doesn't Exist"
        )
    if not pwd_cxt.verify(request.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Activate Account"
        )

    token = JWTToken(user.id)

    return {
        "access_token": token.get_access_token(),
        "refresh_token": token.get_refresh_token(),
        "user_id": user.id,
        "token_type": "bearer",
    }


@router.post("/refresh", response_model=AccessTokenPayload)
async def refresh_access_token(
    refresh_token: TokenPayload = Depends(verify_refresh_token),
):
    """
    Refresh the access token. refresh token should be in header.

    Returns:
        The new access token.
    """
    token = JWTToken(refresh_token.user_id)
    access_token = token.get_access_token()
    return {"access_token": access_token}


@router.get("/verify-email", response_model=MessageResponse)
async def verify_email(
    one_time_token: TokenPayload = Depends(verify_one_time_token),
    session: AsyncSession = Depends(get_db),
):
    """
    Verify the email address of a user. Use one time token obtained from email message in header.

    Returns:
        A message indicating the account activation status.
    """
    statement = select(User).where(User.id == one_time_token.user_id)
    result = await session.exec(statement)
    user = result.one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = True
    session.add(user)
    await session.commit()

    return {"message": "User successfully activated"}


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    payload: PasswordChange,
    user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Change the password for the authenticated user.

    Returns:
        A message indicating the password change status.
    """
    if not pwd_cxt.verify(payload.old_password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect old password"
        )

    user.password = pwd_cxt.hash(payload.new_password)
    session.add(user)
    await session.commit()

    return {"message": "Password updated successfully"}


@router.get("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    email: EmailStr,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db),
):
    """
    Request a password reset. Generates a reset link with one time token and sends it to the user's email.

    Returns:
        A message indicating the password reset email status.
    """
    statement = select(User).where(User.email == email)
    result = await session.exec(statement)
    user = result.one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User with this email does not exist")

    token = JWTToken(user.id).get_one_time_token()
    background_tasks.add_task(send_password_reset_email, user.email, token)

    return {"message": "Password reset email sent successfully"}


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    password: PasswordReset,
    token: TokenPayload = Depends(verify_one_time_token),
    session: AsyncSession = Depends(get_db),
) -> dict:
    """
    Reset the password using a valid one-time token.

    Returns:
        A message indicating the password reset status.
    """
    statement = select(User).where(User.id == token.user_id)
    result = await session.exec(statement)
    user = result.one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password = pwd_cxt.hash(password.new_password)
    session.add(user)
    await session.commit()

    return {"message": "Password reset successfully"}
