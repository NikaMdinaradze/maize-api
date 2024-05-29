from pydantic import UUID4, BaseModel


class TokenPayload(BaseModel):
    """
    Model representing the payload of a JWT token.

    Attributes:
        token_type (str): The type of the token, e.g., "access", "refresh", "one-time".
        user_id (UUID4): The unique identifier of the user associated with the token.
    """

    token_type: str
    user_id: UUID4
