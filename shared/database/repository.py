"""
Base repository for working with the database.
Implements the Repository pattern for abstraction of access to data.
"""

import uuid
from typing import Any, Generic, List, Optional, Type, TypeVar

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Base repository with CRUD operations.
    Provides common methods for working with any model.
    """

    def __init__(self, model: Type[ModelType], session: AsyncSession):
        """
        Initialization of the repository.

        Args:
            model: Class of the SQLAlchemy model
            session: Async session of the DB
        """
        self.model = model
        self.session = session

    async def get_by_id(self, id: uuid.UUID) -> Optional[ModelType]:
        """
        Get a record by ID.

        Args:
            id: UUID of the record

        Returns:
            Optional[ModelType]: Found record or None
        """
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """
        Get all records with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            List[ModelType]: List of records
        """
        result = await self.session.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_ids(self, ids: List[uuid.UUID]) -> List[ModelType]:
        """
        Get records by list of IDs.

        Args:
            ids: List of UUIDs

        Returns:
            List[ModelType]: List of found records
        """
        result = await self.session.execute(
            select(self.model).where(self.model.id.in_(ids))
        )
        return list(result.scalars().all())

    async def create(self, obj_in: dict[str, Any]) -> ModelType:
        """
        Create a new record.

        Args:
            obj_in: Dictionary with data for creation

        Returns:
            ModelType: Created record
        """
        db_obj = self.model(**obj_in)
        self.session.add(db_obj)
        await self.session.flush()
        await self.session.refresh(db_obj)
        return db_obj

    async def update(
        self, id: uuid.UUID, obj_in: dict[str, Any]
    ) -> Optional[ModelType]:
        """
        Update a record.

        Args:
            id: UUID of the record
            obj_in: Dictionary with data for update

        Returns:
            Optional[ModelType]: Updated record or None
        """
        await self.session.execute(
            update(self.model).where(self.model.id == id).values(**obj_in)
        )
        await self.session.flush()
        return await self.get_by_id(id)

    async def delete(self, id: uuid.UUID) -> bool:
        """
        Delete a record.

        Args:
            id: UUID of the record

        Returns:
            bool: True if the record is deleted
        """
        result = await self.session.execute(
            delete(self.model).where(self.model.id == id)
        )
        await self.session.flush()
        return result.rowcount > 0

    async def exists(self, id: uuid.UUID) -> bool:
        """
        Check the existence of a record.

        Args:
            id: UUID of the record

        Returns:
            bool: True if the record exists
        """
        result = await self.session.execute(
            select(func.count()).select_from(self.model).where(self.model.id == id)
        )
        return result.scalar_one() > 0

    async def count(self) -> int:
        """
        Get the number of records.

        Returns:
            int: Number of records
        """
        result = await self.session.execute(
            select(func.count()).select_from(self.model)
        )
        return result.scalar_one()

    async def bulk_create(self, objects: List[dict[str, Any]]) -> List[ModelType]:
        """
        Bulk creation of records.

        Args:
            objects: List of dictionaries with data

        Returns:
            List[ModelType]: List of created records
        """
        db_objects = [self.model(**obj) for obj in objects]
        self.session.add_all(db_objects)
        await self.session.flush()
        return db_objects

    async def bulk_update(self, updates: List[dict[str, Any]]) -> None:
        """
        Bulk update of records.

        Args:
            updates: List of dictionaries with data (must contain 'id')
        """
        for update_data in updates:
            id = update_data.pop("id")
            await self.session.execute(
                update(self.model).where(self.model.id == id).values(**update_data)
            )
        await self.session.flush()

    async def bulk_delete(self, ids: List[uuid.UUID]) -> int:
        """
        Bulk deletion of records.

        Args:
            ids: List of UUIDs for deletion

        Returns:
            int: Number of deleted records
        """
        result = await self.session.execute(
            delete(self.model).where(self.model.id.in_(ids))
        )
        await self.session.flush()
        return result.rowcount
