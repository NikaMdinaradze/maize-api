from typing import List

from fastapi import APIRouter, Depends
from pydantic import UUID4, BaseModel

from src.deps import get_current_user
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
async def update_user(user_data: UserCreate, user: User = Depends(get_current_user)):
    await user.update_from_dict(user_data.dict()).save()
    updated_user = await UserView.from_queryset_single(User.get(id=user.id))
    return updated_user


@router.delete("/me", response_model=Status)
async def delete_user(user: User = Depends(get_current_user)):
    await user.delete()
    return Status(message=f"Deleted user {user.id}")
