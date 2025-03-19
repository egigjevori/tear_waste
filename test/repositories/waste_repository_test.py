from datetime import datetime

import asyncpg

from app.models.waste import WasteEntry
from app.repositories.waste_repository import WasteRepository


async def test_create_waste_entry(db_test_pool: asyncpg.Pool):
    # Arrange
    async with db_test_pool.acquire() as conn:
        repo = WasteRepository(conn)
        waste_entry = WasteEntry(
            type="Plastic",
            weight=2.5,
            timestamp=datetime.now(),
            user_id=1,
        )

        # Act
        created_entry = await repo.create(waste_entry)

        # Assert
        assert created_entry.id is not None

        # Verify the entry exists in the database
        row = await conn.fetchrow("SELECT * FROM waste_entries WHERE id = $1", created_entry.id)
        assert row is not None
        assert row["type"] == "Plastic"
        assert row["weight"] == 2.5
        assert row["user_id"] == 1


async def test_read_waste_entry(db_test_pool: asyncpg.Pool):
    # Arrange
    async with db_test_pool.acquire() as conn:
        repo = WasteRepository(conn)
        waste_entry = WasteEntry(
            type="Plastic",
            weight=2.5,
            timestamp=datetime.now(),
            user_id=1,
        )

        # First, create a waste entry to ensure there is something to read
        created_entry = await repo.create(waste_entry)

        # Act
        read_entry = await repo.read(created_entry.id)

        # Assert
        assert read_entry is not None
        assert read_entry.id == created_entry.id
        assert read_entry.type == "Plastic"
        assert read_entry.weight == 2.5
        assert read_entry.user_id == 1


async def test_delete_waste_entry(db_test_pool: asyncpg.Pool):
    # Arrange
    async with db_test_pool.acquire() as conn:
        repo = WasteRepository(conn)
        waste_entry = WasteEntry(
            type="Plastic",
            weight=2.5,
            timestamp=datetime.now(),
            user_id=1,
        )

        # Create a waste entry to delete
        created_entry = await repo.create(waste_entry)

        # Act
        await repo.delete(created_entry.id)

        # Assert
        # Verify the entry no longer exists in the database
        row = await conn.fetchrow("SELECT * FROM waste_entries WHERE id = $1", created_entry.id)
        assert row is None
