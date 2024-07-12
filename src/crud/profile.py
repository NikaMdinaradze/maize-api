from uuid import UUID

from fastapi import HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.crud.base import BaseCRUD
from src.models import Profile


class ProfileCrud(BaseCRUD):
    async def get_object(self, pk: UUID, session: AsyncSession) -> Profile:
        """
        Retrieve a profile by its users primary key. Overridden base get object.
        """
        statement = select(self.model).where(self.model.user_id == pk)
        result = await session.exec(statement)
        profile = result.first()
        if profile is None:
            raise HTTPException(status_code=404, detail="Object not found")
        return profile  # noqa


profile_manager = ProfileCrud(Profile)
