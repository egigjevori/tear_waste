from contextlib import asynccontextmanager
from typing import AsyncIterator

from app.models.teams import Team
from app.repositories.team_repository import TeamRepository
from app.utils.db import get_db_pool


@asynccontextmanager
async def get_team_repo() -> AsyncIterator[TeamRepository]:
    async with get_db_pool().acquire() as conn:
        async with conn.transaction() as transaction:
            yield TeamRepository(transaction)  # type: ignore


async def create_team(name: str) -> Team:
    async with get_team_repo() as repo:
        team = Team(name=name)
        team = await repo.create(team)
        return team
