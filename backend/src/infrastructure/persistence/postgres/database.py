"""
Database configuration and session management.

Provides async SQLAlchemy session factory.
"""
from typing import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    AsyncEngine,
    async_sessionmaker,
)
from sqlalchemy.pool import NullPool

from .models import Base


class Database:
    """
    Database connection manager.

    Handles SQLAlchemy engine and session lifecycle.
    """

    def __init__(self, database_url: str, echo: bool = False):
        """
        Initialize database connection.

        Args:
            database_url: PostgreSQL connection string
                          (e.g., "postgresql+asyncpg://user:pass@localhost/dbname")
            echo: Whether to log SQL queries (debug mode)
        """
        self.engine: AsyncEngine = create_async_engine(
            database_url,
            echo=echo,
            poolclass=NullPool,  # Disable connection pooling for simplicity
            # In production, use proper pool settings:
            # pool_size=20,
            # max_overflow=10,
            # pool_pre_ping=True,
        )

        self.session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,  # Keep objects accessible after commit
        )

    async def create_tables(self) -> None:
        """
        Create all tables in the database.

        WARNING: Only use in development! In production, use Alembic migrations.
        """
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_tables(self) -> None:
        """
        Drop all tables in the database.

        WARNING: Destructive operation! Only use in tests.
        """
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    async def close(self) -> None:
        """Close database connections."""
        await self.engine.dispose()

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get a new database session.

        Usage:
            async with db.session() as session:
                result = await session.execute(select(OrderModel))
                await session.commit()
        """
        session: AsyncSession = self.session_factory()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    def get_session_factory(self) -> async_sessionmaker[AsyncSession]:
        """Get the session factory for dependency injection."""
        return self.session_factory


# Dependency for FastAPI
async def get_db_session(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency to get a database session.

    Usage:
        @app.post("/orders")
        async def create_order(
            session: AsyncSession = Depends(get_db_session)
        ):
            ...
    """
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
