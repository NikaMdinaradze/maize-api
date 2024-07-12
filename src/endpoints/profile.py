from uuid import UUID

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from src.crud.profile import profile_manager
from src.deps import get_current_active_user, get_db
from src.models import Profile

router = APIRouter(
    prefix="/profile", tags=["profile"], dependencies=(Depends(get_current_active_user),)
)


@router.get("/{pk}", response_model=Profile)
async def get_profile(pk: UUID, session: AsyncSession = Depends(get_db)) -> Profile:
    """
    Retrieve the profile of the currently authenticated user.
    """
    profile = await profile_manager.get_object(pk, session)
    return profile
