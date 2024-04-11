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
    def __init__(self, user_id: UUID4) -> None:
        self.user_id = str(user_id)

    def _create_jwt_token(self, expires_delta: timedelta, token_type: str):
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode = {"user_id": self.user_id, "exp": expire, "token_type": token_type}
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @property
    def access_token(self):
        token = self._create_jwt_token(
            expires_delta=ACCESS_TOKEN_EXPIRATION, token_type="access"
        )
        return token

    @property
    def refresh_token(self):
        token = self._create_jwt_token(
            expires_delta=REFRESH_TOKEN_EXPIRATION, token_type="refresh"
        )
        return token

    @property
    def one_time_token(self):
        token = self._create_jwt_token(
            expires_delta=ONE_TIME_TOKEN_EXPIRATION, token_type="one_time"
        )
        return token
