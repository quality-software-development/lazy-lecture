import os
import pytest
import asyncpg
import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from fastapi.testclient import TestClient

from source.main import app
from ..core.settings import Settings, get_settings


TEST_DB_NAME = "test_market"


class TestSettings(Settings):
    POSTGRES_DB: str = TEST_DB_NAME


def override_get_settings() -> TestSettings:
    return TestSettings()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db():
    settings = get_settings()
    fixed_db_uri = f"postgresql://{settings.POSTGRES_URI}"
    test_db_uri = fixed_db_uri.replace(settings.POSTGRES_DB, TEST_DB_NAME)
    admin_db_uri = fixed_db_uri.replace(settings.POSTGRES_DB, "postgres")

    conn = await asyncpg.connect(dsn=admin_db_uri)
    try:
        await conn.execute(f"DROP DATABASE IF EXISTS {TEST_DB_NAME}")
    except Exception:
        pass
    await conn.execute(f"CREATE DATABASE {TEST_DB_NAME}")
    await conn.close()

    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    ALEMBIC_INI_PATH = os.path.join(BASE_DIR, "alembic.ini")
    alembic_cfg = Config(str(ALEMBIC_INI_PATH))
    alembic_cfg.set_main_option("script_location", "source/migrations")
    # alembic_cfg.set_main_option("script_location", "../migrations")
    alembic_cfg.set_main_option("sqlalchemy.url", test_db_uri)
    command.upgrade(alembic_cfg, "head")

    yield

    conn = await asyncpg.connect(dsn=admin_db_uri)
    await conn.execute(
        f"""
        SELECT pg_terminate_backend(pid)
        FROM pg_stat_activity
        WHERE datname = '{TEST_DB_NAME}' AND pid <> pg_backend_pid();
    """
    )
    await conn.execute(f"DROP DATABASE IF EXISTS {TEST_DB_NAME}")
    await conn.close()


@pytest_asyncio.fixture(autouse=True)
async def clean_tables():
    settings = get_settings()
    fixed_db_uri = f"postgresql://{settings.POSTGRES_URI}"
    test_db_uri = fixed_db_uri.replace(settings.POSTGRES_DB, TEST_DB_NAME)
    conn = await asyncpg.connect(dsn=test_db_uri)
    rows = await conn.fetch(
        "SELECT tablename FROM pg_tables WHERE schemaname = 'public' AND tablename <> 'alembic_version';"
    )
    table_names = [row["tablename"] for row in rows]
    if table_names:
        query = "TRUNCATE TABLE " + ", ".join([f'"{t}"' for t in table_names]) + " RESTART IDENTITY CASCADE;"
        await conn.execute(query)
    await conn.close()
    yield


@pytest.fixture
def application():
    app.dependency_overrides[get_settings] = override_get_settings
    return app


@pytest_asyncio.fixture
async def async_client(application):
    transport = ASGITransport(app=application)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
