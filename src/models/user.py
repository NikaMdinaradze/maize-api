from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True, index=True)
    email: str = Field(max_length=50, unique=True, nullable=False)
    password: str = Field(max_length=128, nullable=False)
    is_active: bool = Field(default=False)
