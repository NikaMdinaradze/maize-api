from sqlmodel import SQLModel


class MessageResponse(SQLModel):
    message: str
