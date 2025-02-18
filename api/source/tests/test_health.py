from source.core.schemas import HealthSchema
import pytest


@pytest.mark.asyncio
async def test_health_is_good(async_client):
    response = await async_client.get("/")
    assert response.status_code == 200
    assert HealthSchema(**response.json()) == HealthSchema(api=True, database=True)
