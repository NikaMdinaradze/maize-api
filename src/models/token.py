from pydantic import UUID4, BaseModel


class TokenPayload(BaseModel):
    token_type: str
    user_id: UUID4
