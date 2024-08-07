from pydantic import UUID4
from sqlmodel import SQLModel


class TokenPayload(SQLModel):
    """
    Model representing the payload of a JWT token.

    Attributes:
        token_type (str): The type of the token, e.g., "access", "refresh", "one-time".
        user_id (UUID4): The unique identifier of the user associated with the token.
    """

    token_type: str
    user_id: UUID4


class AccessTokenPayload(SQLModel):
    """
    Model representing the payload of an access token.

    Attributes:
        access_token (str): The access token string.
        token_type (str): The type of token. Defaults to "bearer".
    """

    access_token: str
    token_type: str = "bearer"


class LoginResponsePayload(AccessTokenPayload):
    """
    Model representing the payload of both access and refresh tokens.

    Inherits:
        AccessTokenPayload: Model representing the payload of an access token.

    Attributes:
        refresh_token (str): The refresh token string.
    """

    refresh_token: str
    user_id: UUID4
