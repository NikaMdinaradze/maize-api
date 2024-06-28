from sqlmodel.ext.asyncio.session import AsyncSession

from src.models.user import User
from src.settings import pwd_cxt


async def create_user(
    db_session: AsyncSession, email: str, password: str, is_active: bool = False
) -> User:
    hashed_password = pwd_cxt.hash(password)
    db_user = User(email=email, password=hashed_password, is_active=is_active)
    db_session.add(db_user)
    await db_session.commit()
    await db_session.refresh(db_user)
    return db_user
