from typing import Generic, Sequence, Type, TypeVar
from uuid import UUID

from fastapi import HTTPException
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

T = TypeVar("T", bound=SQLModel)


class BaseCRUD(Generic[T]):
    def __init__(self, model: Type[T]):
        """
        Initialize the CRUD object with the SQLModel model.
        """
        self.model = model

    async def create(self, data: T, session: AsyncSession) -> T:
        """
        Create a new object in the database.
        """
        obj = self.model.model_validate(data)
        session.add(obj)
        await session.commit()
        await session.refresh(obj)
        return obj

    async def get_object(self, pk: UUID, session: AsyncSession) -> T:
        """
        Retrieve an object by its primary key.
        """
        obj = await session.get(self.model, pk)
        if obj is None:
            raise HTTPException(status_code=404, detail="Object not found")
        return obj

    async def update(self, pk: UUID, data: T, session: AsyncSession) -> T:
        """
        Update an existing object in the database.
        """
        db_obj = await self.get_object(pk, session)
        dump_data = data.model_dump(exclude_unset=True)
        db_obj.sqlmodel_update(dump_data)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def delete(self, pk: UUID, session: AsyncSession) -> bool:
        """
        Delete an object from the database.
        """
        db_obj = await self.get_object(pk, session)
        await session.delete(db_obj)
        await session.commit()
        return True

    async def list(
        self, session: AsyncSession, skip: int = 0, limit: int = 100
    ) -> Sequence[T]:
        """
        List objects from the database with optional pagination.
        """
        result = await session.exec(select(self.model).offset(skip).limit(limit))
        return result.all()
