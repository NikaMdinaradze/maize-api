from uuid import UUID, uuid4

from pydantic import EmailStr
from sqlmodel import Field, SQLModel, AutoString


class UserBase(SQLModel):
    email: EmailStr = Field(max_length=50, unique=True, sa_type=AutoString)

class UserCreate(UserBase):
    password: str = Field(max_length=128)

class UserView(UserBase):
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    is_active: bool = Field(default=False)

class User(UserCreate, UserView, table=True):
    pass

class UserUpdate(SQLModel):
    email: EmailStr | None = None
    password: str | None = None