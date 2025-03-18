from abc import ABC, abstractmethod
from typing import List, Optional
from app.models.teams import Team  # Assuming you have a Team model defined
from app.repositories import Repository
from app.utils.db import fetchrow


class AbstractTeamRepository(Repository):
    @abstractmethod
    async def create(self, team: Team) -> Team:
        """Create a new team."""
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
