from typing import Type, Any

from tortoise.models import Model
from pydantic import BaseModel

from src.models.user import User, UserView, UserCreate

tortoise_models: list[Type[Model]] = [User,]

schemas: list [Type[BaseModel]] = [UserView, UserCreate]

__all__: list[Any] = tortoise_models + schemas

