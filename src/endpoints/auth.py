from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from src.JWT import JWTToken
from src.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


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
