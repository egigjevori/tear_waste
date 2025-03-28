from abc import abstractmethod
from typing import List, Optional

from app.models.waste import WasteEntry
from app.repositories import Repository
from app.utils import cache
from app.utils.db import execute, fetch, fetchrow


class AbstractWasteRepository(Repository):

    @abstractmethod
    async def create(self, waste_entry: WasteEntry) -> WasteEntry:
        raise NotImplementedError

    @abstractmethod
    async def read(self, entry_id: int) -> Optional[WasteEntry]:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, entry_id: int) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_waste_by_user_id(self, user_id: int) -> List[WasteEntry]:
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
            return WasteEntry.from_dict(row)
        return None

    async def delete(self, entry_id: int) -> None:
        query = """
        DELETE FROM waste_entries
        WHERE id = $1
        """
        await execute(self.conn, query, entry_id)

    async def get_waste_by_user_id(self, user_id: int) -> List[WasteEntry]:
        query = """
        SELECT *
        FROM waste_entries
        WHERE user_id = $1
        """
        rows = await fetch(self.conn, query, user_id)
        waste_entries = self._rows_to_entries(rows)
        return waste_entries

    @staticmethod
    def _rows_to_entries(rows) -> List[WasteEntry]:
        return [WasteEntry.from_dict(row) for row in rows]


class CacheWasteRepository(WasteRepository):
    async def create(self, waste_entry: WasteEntry) -> WasteEntry:
        result = await super().create(waste_entry)
        await cache.set_value(f"waste:{result.id}", result.to_dict())
        return result

    async def read(self, entry_id: int) -> Optional[WasteEntry]:
        cache_key = f"waste:{entry_id}"
        cached_data = await cache.get_value(cache_key)
        if cached_data is not None:
            return WasteEntry.from_dict(cached_data)
        else:
            result = await super().read(entry_id)
            if result:
                await cache.set_value(cache_key, result.to_dict())
            return result

    async def delete(self, entry_id: int) -> None:
        entry = await self.read(entry_id)
        await super().delete(entry_id)
        await cache.delete_key(f"waste:{entry_id}")
        await cache.delete_key(f"waste_by_user_id:{entry.user_id}")

    async def get_waste_by_user_id(self, user_id: int) -> List[WasteEntry]:
        cache_key = f"waste_by_user_id:{user_id}"
        cached_data = await cache.get_value(cache_key)
        if cached_data is not None:
            return [WasteEntry.from_dict(data) for data in cached_data]
        else:
            results = await super().get_waste_by_user_id(user_id)
            if results:
                await cache.set_value(cache_key, [result.to_dict() for result in results])
            return results
