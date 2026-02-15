"""
Database engine configuration
"""

import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from config.settings import env

logger = logging.getLogger(__name__)

Base = declarative_base()

db_engine = create_async_engine(
    url=env.database_url,
    echo=env.sql_echo,
    pool_size=env.db_pool_size,
    max_overflow=env.db_max_overflow,
    pool_recycle=env.db_pool_recycle,
    pool_timeout=env.db_pool_timeout,
    pool_pre_ping=True,  # Verify connections before using
    future=True,
)

# Create async session maker
AsyncSessionLocal = async_sessionmaker(
    bind=db_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database sessions
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database - create all tables"""
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created successfully")


async def close_db() -> None:
    """Close database connections"""
    await db_engine.dispose()
    logger.info("Database connections closed")
