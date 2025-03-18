# conftest.py

import os
from contextlib import asynccontextmanager
from typing import AsyncIterator, List, Optional
from unittest.mock import patch

import asyncpg
import pytest
from dotenv import load_dotenv

from app.models.teams import Team
from app.repositories.team_repository import AbstractTeamRepository
from app.utils.db import initdb

# Load environment variables from a .env file
load_dotenv(dotenv_path=".env.test")


async def drop_tables(pool: asyncpg.Pool):
    async with pool.acquire() as conn:
        conn: asyncpg.Connection = conn
        for table in ["waste_entries", "users", "teams"]:
            await conn.execute(f"drop table if exists {table}; ")


@pytest.fixture
async def db_test_pool() -> asyncpg.Pool:
    """Create an asyncpg connection pool."""
    pool = await asyncpg.create_pool(
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        database=os.getenv("POSTGRES_DB"),
        host=os.getenv("POSTGRES_HOST"),
        min_size=1,  # Minimum number of connections in the pool
        max_size=10,  # Maximum number of connections in the pool
    )
    await initdb(pool)
    yield pool
    await drop_tables(pool)
    await pool.close()


@pytest.fixture
def patch_get_db_pool(db_test_pool):
    """Patch the get_db_pool function to return the test pool."""
    with patch("app.services.team_service.get_db_pool", return_value=db_test_pool):
        yield


# TODO improve with hashmap
class FakeTeamRepository(AbstractTeamRepository):
    def __init__(self, _):
        self.teams = []
        self.next_id = 1

    async def create(self, team: Team) -> Team:
        team.id = self.next_id
        self.next_id += 1
        self.teams.append(team)
        return team

    async def read(self, team_id: int) -> Optional[Team]:
        for team in self.teams:
            if team.id == team_id:
                return team
        return None

    async def delete(self, team_id: int) -> None:
        self.teams = [team for team in self.teams if team.id != team_id]


@pytest.fixture
def team_repo_mock():
    with patch(
        "app.services.team_service.TeamRepository", new=FakeTeamRepository
    ) as mock_repo:
        yield mock_repo


@asynccontextmanager
async def get_team_repo() -> AsyncIterator[AbstractTeamRepository]:
    repo = FakeTeamRepository(None)
    yield repo


@pytest.fixture
def get_team_repo_mock():
    with patch(
        "app.services.team_service.get_team_repo", wraps=get_team_repo
    ) as mock_repo:
        yield mock_repo
