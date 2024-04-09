from tortoise.models import Model
from src.models.user import User, UserBase, UserCreate

__all__: list[Model] = [User, UserBase, UserCreate]
