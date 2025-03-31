from abc import abstractmethod
from typing import Optional

from app.models.teams import Team
from app.repositories import Repository
from app.utils import cache
from app.utils.db import fetchrow


class AbstractTeamRepository(Repository):
    @abstractmethod
    async def create(self, team: Team) -> Team:
        raise NotImplementedError

    @abstractmethod
    async def read(self, team_id: int) -> Optional[Team]:
        raise NotImplementedError

    @abstractmethod
    async def read_all(self) -> list[Team]:
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

    async def read_all(self) -> list[Team]:
        query = """
        SELECT *
        FROM teams
        """
        rows = await self.conn.fetch(query)
        return [Team.from_dict(row) for row in rows]


class CacheTeamRepository(TeamRepository):

    async def create(self, team: Team) -> Team:
        result = await super().create(team)
        await cache.set_value(f"team:{result.id}", result.to_dict())
        await cache.delete_key("all_teams")
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

    async def read_all(self) -> list[Team]:
        # Attempt to retrieve all teams from cache
        cached_teams = await cache.get_value("all_teams")
        if cached_teams is not None:
            return [Team.from_dict(team) for team in cached_teams]

        # If not in cache, retrieve from database and cache the result
        teams = await super().read_all()
        await cache.set_value("all_teams", [team.to_dict() for team in teams])
        return teams
