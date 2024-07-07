from typing import Tuple, Type

from src.models.user import User, UserCreate, UserView, UserBase, PasswordChange, PasswordReset
from src.models.token import TokenPayload, AccessTokenPayload, LoginResponsePayload
from src.models.utils import MessageResponse

from sqlmodel import SQLModel

table_models: Tuple[Type[SQLModel], ...] = (User, )

schema_models: Tuple[Type[SQLModel], ...] = (
    UserCreate, UserView, UserBase, TokenPayload,
    AccessTokenPayload, LoginResponsePayload, MessageResponse,
    PasswordChange, PasswordReset
)