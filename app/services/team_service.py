from contextlib import asynccontextmanager
from typing import AsyncIterator

from app.models.teams import Team
from app.repositories.team_repository import TeamRepository
from app.utils.db import get_db_pool


@asynccontextmanager
async def get_team_repo() -> AsyncIterator[TeamRepository]:
    async with get_db_pool().acquire() as conn:
        yield TeamRepository(conn)  # type: ignore


async def create_team(name: str) -> Team:
    async with get_team_repo() as repo:
        team = Team(name=name)
        team = await repo.create(team)
        return team


async def get_team(team_id: int) -> Team:
    async with get_team_repo() as repo:
        team = await repo.read(team_id)
        return team


async def assert_team_exists(team_id: int) -> None:
    team = await get_team(team_id)
    if not team:
        raise ValueError(f"Team {team_id} does not exist")
