from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from app.models.teams import Team
from app.repositories.team_repository import TeamRepository, CacheTeamRepository
from app.utils.db import get_db_pool

logger = logging.getLogger(__name__)


@asynccontextmanager
async def get_team_repo() -> AsyncIterator[TeamRepository]:
    async with get_db_pool().acquire() as conn:
        # yield TeamRepository(conn)  # type: ignore
        yield CacheTeamRepository(conn)  # type: ignore


async def create_team(name: str) -> Team:
    logger.info(f"Creating team with name: {name}")

    async with get_team_repo() as repo:
        team = Team(name=name)
        team = await repo.create(team)

        logger.info(f"Team created with ID: {team.id} and name: {team.name}")
        return team


async def get_team(team_id: int) -> Team | None:
    logger.info(f"Fetching team with ID: {team_id}")

    async with get_team_repo() as repo:
        team = await repo.read(team_id)

        if team:
            logger.info(f"Found team with ID: {team.id} and name: {team.name}")
        else:
            logger.warning(f"Team with ID: {team_id} not found")

        return team


async def assert_team_exists(team_id: int) -> None:
    team = await get_team(team_id)
    if not team:
        logger.error(f"Team {team_id} does not exist")
        raise ValueError(f"Team {team_id} does not exist")
