from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    email: str = Field(max_length=50, unique=True, nullable=False)


class UserCreate(UserBase):
    password: str = Field(max_length=128, nullable=False)


class UserView(UserBase):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True, index=True)
    is_active: bool = False


class User(UserCreate, UserView, table=True):
    pass


class UserUpdate(SQLModel):
    email: str | None = None
    password: str | None = None
