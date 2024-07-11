from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession

from src.JWT import JWTToken
from src.models import Profile
from tests.utils import create_user


async def test_get_profile(client: AsyncClient, db_session: AsyncSession) -> None:
    """
    Test retrieving the profile.
    """
    email = "user@example.com"
    password = "Password123"
    user = await create_user(db_session, email, password, is_active=True)

    profile = Profile(user=user)
    db_session.add(profile)
    await db_session.commit()

    token = JWTToken(user.id).get_access_token()

    response = await client.get(
        "/profile/me", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    profile_data = response.json()
    assert profile_data.get("user_id") == str(user.id)
    assert isinstance(profile_data.get("picture"), str)
    assert isinstance(profile_data.get("username"), str)


async def test_get_profile_unauthorized(client: AsyncClient) -> None:
    """
    Test retrieving the profile without authentication.
    """
    response = await client.get("/profile/me")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}
