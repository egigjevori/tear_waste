from contextlib import asynccontextmanager
from typing import AsyncIterator, List

from app.models.users import User, UserRole
from app.models.waste import WasteEntry
from app.repositories.user_repository import UserRepository
from app.repositories.waste_repository import WasteRepository
from app.services import user_service, team_service
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
    await user_service.assert_user_exists(user_id)
    waste = WasteEntry(
        type=type,
        weight=weight,
        user_id=user_id,
    )

    async with get_waste_repo() as repo:
        entry = await repo.create(waste)
        return entry


async def get_waste_by_user_id(user_id: int) -> List[WasteEntry]:
    await user_service.assert_user_exists(user_id)
    async with get_waste_repo() as repo:
        waste_entries = await repo.get_waste_by_user_id(user_id)
        return waste_entries


async def get_waste_by_team_id(team_id: int) -> List[WasteEntry]:
    await team_service.assert_team_exists(team_id)
    async with get_waste_repo() as repo:
        waste_entries = await repo.get_waste_by_team_id(team_id)
        return waste_entries
