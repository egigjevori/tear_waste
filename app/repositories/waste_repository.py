from abc import abstractmethod
from typing import Optional

from app.models.waste import WasteEntry
from app.repositories import Repository
from app.utils.db import execute_query, fetchrow


class AbstractWasteRepository(Repository):

    @abstractmethod
    async def create(self, waste_entry: WasteEntry) -> WasteEntry:
        """Create a new waste entry."""
        raise NotImplementedError

    @abstractmethod
    async def read(self, entry_id: int) -> Optional[WasteEntry]:
        """Read a waste entry by its ID."""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, entry_id: int) -> None:
        """Delete a waste entry by its ID."""
        raise NotImplementedError


class WasteRepository(AbstractWasteRepository):
    async def create(self, waste_entry: WasteEntry) -> WasteEntry:
        query = """
        INSERT INTO waste_entries (type, weight, timestamp, user_id)
        VALUES ($1, $2, $3, $4)
        RETURNING id
        """
        row = await fetchrow(
            self.conn,
            query,
            waste_entry.type,
            waste_entry.weight,
            waste_entry.timestamp,
            waste_entry.user_id,
        )
        waste_entry.id = row["id"]
        return waste_entry

    async def read(self, entry_id: int) -> Optional[WasteEntry]:
        query = """
        SELECT *
        FROM waste_entries
        WHERE id = $1
        """
        row = await fetchrow(self.conn, query, entry_id)
        if row:
            return WasteEntry(
                id=row["id"],
                type=row["type"],
                weight=row["weight"],
                timestamp=row["timestamp"],
                user_id=row["user_id"],
            )
        return None

    async def delete(self, entry_id: int) -> None:
        query = """
        DELETE FROM waste_entries
        WHERE id = $1
        """
        await execute_query(self.conn, query, entry_id)
