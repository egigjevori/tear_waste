from contextlib import asynccontextmanager
from typing import AsyncIterator

from app.models.users import User, UserRole
from app.models.waste import WasteEntry
from app.repositories.user_repository import UserRepository
from app.repositories.waste_repository import WasteRepository
from app.utils.db import get_db_pool


@asynccontextmanager
async def get_waste_repo() -> AsyncIterator[WasteRepository]:
    async with get_db_pool().acquire() as conn:
        yield WasteRepository(conn)  # type: ignore


async def create_waste(
    type: str,
    weight: float,
    user_id: int,
) -> WasteEntry:
    # TODO validate data
    waste = WasteEntry(
        type=type,
        weight=weight,
        user_id=user_id,
    )

    async with get_waste_repo() as repo:
        entry = await repo.create(waste)
        return entry
