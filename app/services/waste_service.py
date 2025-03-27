import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator, List

from app.models.waste import WasteEntry
from app.repositories.waste_repository import CacheWasteRepository, WasteRepository
from app.services import user_service
from app.utils.db import get_db_pool

logger = logging.getLogger(__name__)


@asynccontextmanager
async def get_waste_repo() -> AsyncIterator[WasteRepository]:
    async with get_db_pool().acquire() as conn:
        # yield WasteRepository(conn)  # type: ignore
        yield CacheWasteRepository(conn)  # type: ignore


async def create_waste(
    type: str,
    weight: float,
    user_id: int,
) -> WasteEntry:
    logger.info(f"Creating waste entry with type: {type}, weight: {weight}, user_id: {user_id}")

    await user_service.assert_user_exists(user_id)
    waste = WasteEntry(
        type=type,
        weight=weight,
        user_id=user_id,
    )

    async with get_waste_repo() as repo:
        entry = await repo.create(waste)

        logger.info(f"Waste entry created with ID: {entry.id} for user_id: {user_id}")
        return entry


async def get_waste_by_user_id(user_id: int) -> List[WasteEntry]:
    logger.info(f"Fetching waste entries for user_id: {user_id}")

    await user_service.assert_user_exists(user_id)
    async with get_waste_repo() as repo:
        waste_entries = await repo.get_waste_by_user_id(user_id)

        logger.info(f"Found {len(waste_entries)} waste entries for user_id: {user_id}")
        return waste_entries
