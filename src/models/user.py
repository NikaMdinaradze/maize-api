import re
from enum import Enum
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from pydantic import EmailStr, field_validator
from sqlalchemy.orm import relationship
from sqlmodel import AutoString, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from src.models import Profile


class RoleEnum(str, Enum):
    """
    Enum representing different user roles.

    Attributes:
        admin (str): Represents an administrative user with full access to the system.
        mentor (str): Represents a mentor user with permissions to manage courses.
        customer (str): Represents a customer user with basic access to use the services.
    """

    admin = "admin"
    mentor = "mentor"
    customer = "customer"


class UserBase(SQLModel):
    """
    Base model representing common attribute(s) for a user.

    Attributes:
        email (EmailStr): The email address of the user.
    """

    email: EmailStr = Field(max_length=50, unique=True, sa_type=AutoString)


class UserCreate(UserBase):
    """
    Model for creating a new user.

    Inherits:
        UserBase: Base model representing common attributes for a user.

    Attributes:
        password (str): The password for the new user.
    """

    password: Optional[str] = Field(None, max_length=24)

    @field_validator("password")
    @classmethod
    def validate_password_field(cls, password: str) -> str:
        return cls.validate_password(password)

    @staticmethod
    def validate_password(password: str) -> str:
        if not password:
            raise ValueError("Password is required field.")
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if not re.search(r"[A-Z]", password):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not re.search(r"\d", password):
            raise ValueError("Password must contain at least one digit.")
        return password


class UserView(UserBase):
    """
    Model for viewing user details without sensitive data.

    Inherits:
        UserBase: Base model representing common attributes for a user.

    Attributes:
        id (UUID): The unique identifier for the user.
        is_active (bool): Flag indicating if the user account is active.
    """

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    role: RoleEnum = RoleEnum.customer
    is_active: bool = Field(default=False)


class User(UserCreate, UserView, table=True):
    """
    Model representing a user in database.

    Inherits:
        UserCreate: Model for creating a new user.
        UserView: Model for viewing user details.
    """

    profile: Optional["Profile"] = Relationship(
        sa_relationship=relationship(
            argument="Profile",
            cascade="delete",
            back_populates="user",
            uselist=False,
        )
    )


class PasswordReset(SQLModel):
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, new_password):
        return UserCreate.validate_password(new_password)


class PasswordChange(PasswordReset):
    old_password: str
