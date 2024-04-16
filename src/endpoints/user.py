from typing import List

from fastapi import APIRouter, Depends
from pydantic import UUID4, BaseModel
from starlette.exceptions import HTTPException

from src.deps import get_current_user, verify_access_token
from src.models import User, UserCreate, UserView

router = APIRouter(prefix="/user", tags=["user"])


class Status(BaseModel):
    message: str


@router.get("/", response_model=List[UserView])
async def get_users():
    return await UserView.from_queryset(User.all())


@router.get("/me", response_model=UserView)
async def user_me(user: User = Depends(get_current_user)):
    return user


@router.get("/{id}", response_model=UserView)
async def get_user(user_id: UUID4):
    return await UserView.from_queryset_single(User.get(id=user_id))


@router.put("/me", response_model=UserView)
async def update_user(user: UserCreate, token: dict = Depends(verify_access_token)):
    user_id = token.get("user_id")
    await User.filter(id=user_id).update(**user.model_dump(exclude_unset=True))
    return await UserView.from_queryset_single(User.get(id=user_id))


@router.delete("/me", response_model=Status)
async def delete_user(token: dict = Depends(verify_access_token)):
    user_id = token.get("user_id")
    deleted_count = await User.filter(id=user_id).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    return Status(message=f"Deleted user {user_id}")
