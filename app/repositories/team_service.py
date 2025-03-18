from typing import List, Optional

from app.models.teams import Team
from app.repositories.team_repository import AbstractTeamRepository


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
