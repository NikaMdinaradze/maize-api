from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

from src.models import User


class Profile(SQLModel, table=True):
    """
    Represents the data required to create a profile.
    """

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    username: str = "default"
    picture: str = "default.png"

    user_id: UUID = Field(default=None, foreign_key="user.id", unique=True)
    user: User = Relationship(back_populates="profile")
