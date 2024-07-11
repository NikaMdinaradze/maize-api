from fastapi import APIRouter, Depends
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.deps import get_current_active_user, get_db
from src.models import Profile, User

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/me", response_model=Profile)
async def get_profile(
    user: User = Depends(get_current_active_user), session: AsyncSession = Depends(get_db)
) -> Profile:
    """
    Retrieve the profile of the currently authenticated user.
    """
    statement = select(Profile).where(Profile.user == user)
    result = await session.exec(statement)
    profile = result.one()
    return profile
