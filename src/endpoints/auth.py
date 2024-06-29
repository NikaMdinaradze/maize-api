from fastapi import APIRouter, BackgroundTasks, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.deps import (
    get_current_active_user,
    get_db,
    verify_one_time_token,
    verify_refresh_token,
)
from src.JWT import JWTToken
from src.models.token import (
    AccessTokenPayload,
    LoginResponsePayload,
    TokenPayload,
)
from src.models.user import PasswordChange, User, UserCreate, UserView
from src.settings import lookup, pwd_cxt
from src.tasks import send_verification_email

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserView)
async def register(
    user: UserCreate,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db),
):
    """
    Register a new user and send verification url (/verify-email).
    If user already exists with same email and is not active resends email
    and if it is active raises error that email already exists.

    Returns:
        The details of the registered user.
    """

    statement = select(User).where(User.email == user.email)
    result = await session.exec(statement)
    db_user = result.one_or_none()

    if db_user and db_user.is_active:
        raise HTTPException(status_code=400, detail="email already exists")
    if not db_user:
        db_user = User(email=user.email, password=pwd_cxt.hash(user.password))
        session.add(db_user)
        await session.commit()
        await session.refresh(db_user)
    token = JWTToken(db_user.id).get_one_time_token()
    background_tasks.add_task(send_verification_email, db_user.email, token)

    return db_user


@router.post("/login", response_model=LoginResponsePayload)
async def login(
    request: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_db),
):
    """
    Authenticate and log in a user.

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
    Refresh the access token.

    Returns:
        The new access token.
    """
    token = JWTToken(refresh_token.user_id)
    access_token = token.get_access_token()
    return {"access_token": access_token}


template = lookup.get_template("successful_activation.html")
success_html = template.render()


@router.get("/verify-email")
async def verify_email(
    one_time_token: TokenPayload = Depends(verify_one_time_token),
    session: AsyncSession = Depends(get_db),
):
    """
    Verify the email address of a user.

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

    return HTMLResponse(content=success_html, status_code=200)


@router.post("/change-password")
async def change_password(
    payload: PasswordChange,
    user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
) -> dict:
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
