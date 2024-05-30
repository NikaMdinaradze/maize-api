from enum import Enum
from uuid import UUID, uuid4

from pydantic import EmailStr
from sqlmodel import AutoString, Field, SQLModel


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

    password: str = Field(max_length=128)


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

    pass


class UserUpdate(SQLModel):
    """
    Model for updating (patch) user details.

    Attributes:
        email (EmailStr | None): The updated email address of the user.
        password (str | None): The updated password of the user.
    """

    email: EmailStr | None = None
    password: str | None = None
