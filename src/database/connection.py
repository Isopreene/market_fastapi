from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import (create_async_engine,
                                    AsyncSession, async_sessionmaker)
from config import settings


settings.configure(ENV_FOR_DYNACONF="production")
SQLALCHEMY_DATABASE_URL = (f"postgresql+asyncpg://"
                           f"{settings.POSTGRES_USER}:"
                           f"{settings.POSTGRES_PASS}@"
                           f"{settings.POSTGRES_HOST}:"
                           f"{settings.POSTGRES_PORT}"
                           f"/{settings.POSTGRES_DB}")


engine = create_async_engine(SQLALCHEMY_DATABASE_URL)
Base = declarative_base()
SessionLocal = async_sessionmaker(bind=engine,
                                  class_=AsyncSession,
                                  autoflush=False,
                                  expire_on_commit=False)


async def get_db() -> AsyncSession:
    """создать сессию"""
    db = SessionLocal()
    async with db:
        yield db
