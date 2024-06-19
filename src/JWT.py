from datetime import datetime, timedelta, timezone

from jose import jwt
from pydantic import UUID4

from src.settings import (
    ACCESS_TOKEN_EXPIRATION,
    ALGORITHM,
    ONE_TIME_TOKEN_EXPIRATION,
    REFRESH_TOKEN_EXPIRATION,
    SECRET_KEY,
)


class JWTToken:
    """
    Utility class for generating JWT tokens.

    Attributes:
        user_id (str): The user ID used to generate tokens.

    Methods:
        access_token: Property method to generate an access token.
        refresh_token: Property method to generate a refresh token.
        one_time_token: Property method to generate a one-time token.
    """

    def __init__(self, user_id: UUID4) -> None:
        """
        Initialize the JWTToken object with user id.

        Args:
            user_id (UUID4): The user ID used to generate tokens.
        """
        self.user_id = str(user_id)

    def _create_jwt_token(self, expires_delta: timedelta, token_type: str):
        """
        Create a JWT token.

        Args:
            expires_delta (timedelta): The expiration time delta for the token.
            token_type (str): The type of token to generate.

        Returns:
            str: The generated JWT token.
        """
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode = {"user_id": self.user_id, "exp": expire, "token_type": token_type}
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def get_access_token(self, expires_delta=ACCESS_TOKEN_EXPIRATION):
        """
        Generate an access token.

        Returns:
            str: The generated access token.
        """
        token = self._create_jwt_token(expires_delta=expires_delta, token_type="access")
        return token

    def get_refresh_token(self, expires_delta=REFRESH_TOKEN_EXPIRATION):
        """
        Generate a refresh token.

        Returns:
            str: The generated refresh token.
        """
        token = self._create_jwt_token(expires_delta=expires_delta, token_type="refresh")
        return token

    def get_one_time_token(self, expires_delta=ONE_TIME_TOKEN_EXPIRATION):
        """
        Generate a one-time token.

        Returns:
            str: The generated one-time token.
        """
        token = self._create_jwt_token(expires_delta=expires_delta, token_type="one-time")
        return token
