import pytest
import asyncio
from sqlalchemy import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from fastapi.testclient import TestClient

from source.core.database import Base
from source.main import app, get_db

DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool,
)


def app_change_db_to_sqlite(app, engine):
    TestingSessionLocal = async_sessionmaker(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    return app


async def init_models(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def teardown_models(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def setup_db(engine):
    asyncio.run(init_models(engine))


def teardown_db(engine):
    asyncio.run(teardown_models(engine))


app = app_change_db_to_sqlite(app, engine)


@pytest.fixture(scope="function")
def client():
    setup_db(engine)
    with TestClient(app) as web_client:
        yield web_client
    teardown_db(engine)
