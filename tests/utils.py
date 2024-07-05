from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlmodel.ext.asyncio.session import AsyncSession

from src.models.user import User
from src.settings import engine, pwd_cxt


async def create_user(
    db_session: AsyncSession, email: str, password: str, is_active: bool = False
) -> User:
    hashed_password = pwd_cxt.hash(password)
    db_user = User(email=email, password=hashed_password, is_active=is_active)
    db_session.add(db_user)
    await db_session.commit()
    await db_session.refresh(db_user)
    return db_user


async def create_test_db(db_name: str) -> None:
    """
    Create test postgres database.
    """
    try:
        # Ensure we're not in a transaction
        async with engine.connect() as connection:
            await connection.execute(text("COMMIT;"))  # Commit any active transaction
            await connection.execute(text(f"CREATE DATABASE {db_name};"))
    except OperationalError as e:
        print(f"Error occurred: {e}")
    finally:
        await engine.dispose()


async def delete_test_db(db_name: str):
    """
    Delete test postgres database.
    """
    try:
        async with engine.connect() as connection:
            await connection.execute(text("COMMIT;"))  # Commit any active transaction
            await connection.execute(text(f"DROP DATABASE {db_name};"))
    except OperationalError as e:
        print(f"Error occurred: {e}")
    finally:
        await engine.dispose()
