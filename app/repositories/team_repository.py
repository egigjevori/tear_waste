from abc import abstractmethod
from typing import Optional

from mypy.reachability import assert_will_always_fail

from app.models.teams import Team  # Assuming you have a Team model defined
from app.repositories import Repository
from app.utils import cache
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

class CacheTeamRepository(TeamRepository):

    async def create(self, team: Team) -> Team:
        result = await super().create(team)
        await cache.set_value(f"team:{result.id}", result.to_dict())
        return result

    async def read(self, team_id: int) -> Optional[Team]:
        cache_key = f"team:{team_id}"
        cached_data = await cache.get_value(cache_key)
        if cached_data is not None:
            return Team.from_dict(cached_data)
        else:
            result = await super().read(team_id)
            if result:
                await cache.set_value(cache_key, result.to_dict())
            return result
