from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from server.utils.config import settings

DB_URL = settings.DB_URL
if not DB_URL:
    raise ValueError("DB_URL is not set")

async_engine: AsyncEngine = create_async_engine(
    DB_URL, 
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    echo=True
)

async_session = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

async def get_session():
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

DBSession = Annotated[AsyncSession, Depends(get_session)]