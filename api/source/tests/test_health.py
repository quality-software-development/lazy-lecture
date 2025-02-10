from source.core.schemas import HealthSchema


def test_health_is_good(client):
    response = client.get("/")
    assert response.status_code == 200
    assert HealthSchema(**response.json()) == HealthSchema(api=True, database=True)
