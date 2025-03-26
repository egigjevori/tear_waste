from abc import abstractmethod
from typing import Optional

from mypy.reachability import assert_will_always_fail

from app.models.teams import Team  # Assuming you have a Team model defined
from app.repositories import Repository
from app.utils.cache import get_value, set_value
from app.utils.db import fetchrow


class AbstractTeamRepository(Repository):
    @abstractmethod
    async def create(self, team: Team) -> Team:
        """Create a new team."""
        raise NotImplementedError

    @abstractmethod
    async def read(self, team_id: int) -> Optional[Team]:
        """Read a team by its ID."""
        raise NotImplementedError


class TeamRepository(AbstractTeamRepository):
    async def create(self, team: Team) -> Team:
        query = """
        INSERT INTO teams (name)
        VALUES ($1)
        RETURNING id
        """
        row = await fetchrow(
            self.conn,
            query,
            team.name,
        )
        team.id = row["id"]
        return team

    async def read(self, team_id: int) -> Optional[Team]:
        query = """
        SELECT *
        FROM teams
        WHERE id = $1
        """
        row = await fetchrow(self.conn, query, team_id)
        if row:
            return Team.from_dict(row)
        return None

class CacheTeamRepository(AbstractTeamRepository):

    async def create(self, team: Team) -> Team:
        return await super().create(team)

    async def read(self, team_id: int) -> Optional[Team]:
        cache_key = f"team_{team_id}"
        cached_data = await get_value(cache_key)
        if cached_data is not None:
            return Team(**cached_data)
        else:
            result = await super().read(team_id)
            if result:
                await set_value(cache_key, result.dict())
            return result