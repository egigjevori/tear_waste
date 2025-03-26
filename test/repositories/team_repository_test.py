import asyncpg
import pytest

from app.models.teams import Team
from app.repositories.team_repository import TeamRepository, CacheTeamRepository


async def test_create_team(db_test_pool: asyncpg.Pool):
    # Arrange
    async with db_test_pool.acquire() as conn:
        repo = TeamRepository(conn)
        team = Team(
            name="Development Team",
        )

        # Act
        created_team = await repo.create(team)

        # Assert
        assert created_team.id is not None

        # Verify the team exists in the database
        row = await conn.fetchrow("SELECT * FROM teams WHERE id = $1", created_team.id)
        assert row is not None
        assert row["name"] == "Development Team"


async def test_cache_team(db_test_pool: asyncpg.Pool):
    # Arrange
    async with db_test_pool.acquire() as conn:
        repo = CacheTeamRepository(conn)
        team = Team(
            name="Development Team",
        )

        # Act
        created_team = await repo.create(team)
        created_team = await repo.read(team.id)
        created_team = await repo.read(team.id)
        created_team = await repo.read(team.id)

        # Assert
        assert created_team.id is not None
