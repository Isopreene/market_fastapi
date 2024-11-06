import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import (AsyncSession,
                                    async_sessionmaker, create_async_engine)
from sqlalchemy.pool import NullPool
from config import settings
from src.database.connection import get_db, Base
from src.app.main import app
import pytest_asyncio


settings.configure(ENV_FOR_DYNACONF="development")
SQLALCHEMY_TEST_DATABASE_URL = (f"postgresql+asyncpg://"
                                f"{settings.POSTGRES_USER}:"
                                f"{settings.POSTGRES_PASS}@"
                                f"{settings.POSTGRES_HOST}:"
                                f"{settings.POSTGRES_PORT}"
                                f"/{settings.POSTGRES_DB}")

engine_test = create_async_engine(SQLALCHEMY_TEST_DATABASE_URL,
                                  poolclass=NullPool,)

async_session_maker = async_sessionmaker(
    engine_test, class_=AsyncSession, expire_on_commit=False,
)


async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


app.dependency_overrides[get_db] = override_get_async_session


@pytest_asyncio.fixture(autouse=True, scope="session")
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# SETUP
@pytest_asyncio.fixture(scope="session")
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        app=app, base_url="http://0.0.0.0:8000/"
    ) as async_client:
        yield async_client
