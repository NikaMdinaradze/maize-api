from tortoise.models import Model
from src.models.user import User, UserView, UserCreate

__all__: list[Model] = [User, UserView, UserCreate]
