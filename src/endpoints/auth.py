from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from src.deps import verify_refresh_token
from src.JWT import JWTToken
from src.models import TokenPayload, User, UserCreate, UserView

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserView)
async def register(user: UserCreate):
    """
    TODO: add send mail verification
    """
    user_obj = await User.create(**user.model_dump(exclude_unset=True))
    return await UserView.from_tortoise_orm(user_obj)


@router.post("/login")
async def login(request: OAuth2PasswordRequestForm = Depends()):
    user = await User.filter(username=request.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User Doesn't Exist"
        )

    if not user.password == request.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials"
        )

    token = JWTToken(user.id)
    return {
        "access_token": token.access_token,
        "refresh_token": token.refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh")
def refresh_access_token(refresh_token: TokenPayload = Depends(verify_refresh_token)):
    token = JWTToken(refresh_token.user_id)
    access_token = token.access_token
    return {"access_token": access_token}
