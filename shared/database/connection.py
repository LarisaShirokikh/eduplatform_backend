"""
Connection to the database using SQLAlchemy async.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from shared.config import db_config


class DatabaseConnection:
    """
    Class for managing the connection to the database.
    Uses async SQLAlchemy for asynchronous operations.
    """

    def __init__(
        self, database_url: str | None = None, service_name: str | None = None
    ):
        """
        Initialization of the connection to the DB.

        Args:
            database_url: URL of the database (optional)
            service_name: Name of the service for getting a specific DB
        """
        # Define the URL of the database
        if database_url:
            self._database_url = database_url
        elif service_name:
            self._database_url = db_config.get_service_db_url(service_name)
        else:
            self._database_url = db_config.database_url

        # Create engine and session maker
        self._engine: AsyncEngine | None = None
        self._session_maker: async_sessionmaker[AsyncSession] | None = None

    @property
    def engine(self) -> AsyncEngine:
        """Get or create async engine."""
        if self._engine is None:
            self._engine = create_async_engine(
                self._database_url,
                **db_config.engine_options,
            )
        return self._engine

    @property
    def session_maker(self) -> async_sessionmaker[AsyncSession]:
        """Get or create session maker."""
        if self._session_maker is None:
            self._session_maker = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autocommit=False,
                autoflush=False,
            )
        return self._session_maker

    async def get_session(self) -> AsyncSession:
        """
        Get a new session of the DB.

        Returns:
            AsyncSession: Session for working with the DB
        """
        return self.session_maker()

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """
            Context manager for working with the session of the DB.

        Yields:
            AsyncSession: Session of the DB

        Example:
            async with db.session() as session:
                result = await session.execute(query)
        """
        session = await self.get_session()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def close(self) -> None:
        """Close the connection to the DB."""
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._session_maker = None

    async def ping(self) -> bool:
        """
        Check the connection to the DB.

        Returns:
            bool: True if the connection is active
        """
        try:
            async with self.session() as session:
                await session.execute("SELECT 1")
            return True
        except Exception:
            return False


# Global instances for each service
_database_connections: dict[str, DatabaseConnection] = {}


def get_database(service_name: str | None = None) -> DatabaseConnection:
    """
    Get the connection to the DB for the service.

    Args:
        service_name: Name of the service (user, course, progress, certificate)

    Returns:
        DatabaseConnection: Connection to the DB

    Example:
        db = get_database("user")
        async with db.session() as session:
            result = await session.execute(query)
    """
    key = service_name or "default"

    if key not in _database_connections:
        _database_connections[key] = DatabaseConnection(service_name=service_name)

    return _database_connections[key]


async def close_all_connections() -> None:
    """Close all connections to the DB."""
    for connection in _database_connections.values():
        await connection.close()
    _database_connections.clear()


# Dependency for FastAPI
async def get_db_session(
    service_name: str | None = None,
) -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI for getting the session of the DB.

    Args:
        service_name: Name of the service

    Yields:
        AsyncSession: Session of the DB

    Example:
        @router.get("/users")
        async def get_users(session: AsyncSession = Depends(get_db_session)):
            result = await session.execute(select(User))
            return result.scalars().all()
    """
    db = get_database(service_name)
    async with db.session() as session:
        yield session
