from pydantic import UUID4, BaseModel, EmailStr


class UserBase(BaseModel):
    username: str
    email: str
    age: int
    first_name: str
    last_name: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: UUID4


class UserUpdate(BaseModel):
    username: str = None
    email: EmailStr = None
    age: int = None
    first_name: str = None
    last_name: str = None
