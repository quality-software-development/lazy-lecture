import pytest
from fastapi.testclient import TestClient

from source.main import app


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as web_client:
        yield web_client
