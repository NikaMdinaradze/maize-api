from httpx import AsyncClient


async def test_root(client: AsyncClient) -> None:
    """
    Test the root URL.
    """
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "root url"}
