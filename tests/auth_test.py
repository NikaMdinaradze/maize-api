from httpx import AsyncClient


async def test_register(client: AsyncClient) -> None:
    payload = {
        "email": "user@example.com",
        "password": "string"
    }
    response = await client.post('/auth/register', json=payload)
    response_data = response.json()
    assert response.status_code == 200
    assert response_data["email"] == payload['email']
    assert "id" in response_data
    assert response_data["role"] == "customer"
    assert response_data["is_active"] is False