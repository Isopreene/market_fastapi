from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession


SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://user:pass@localhost:5432/postgres"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine,
                            class_=AsyncSession,
                            autoflush=False,
                            expire_on_commit=False)


async def get_db() -> AsyncSession:
    """создать сессию"""
    db = SessionLocal()
    async with db:
        yield db
