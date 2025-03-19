# conftest.py
import asyncio
import os
from asyncio import AbstractEventLoop
from contextlib import asynccontextmanager
from typing import AsyncIterator, List, Optional, Iterator, Dict
from unittest.mock import patch

import asyncpg
import pytest
from dotenv import load_dotenv
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.models.teams import Team
from app.models.users import User
from app.models.waste import WasteEntry
from app.repositories.team_repository import AbstractTeamRepository
from app.repositories.user_repository import AbstractUserRepository
from app.repositories.waste_repository import AbstractWasteRepository
from app.utils.db import initdb

# Load environment variables from a .env file
load_dotenv(dotenv_path=".env.test")


@pytest.yield_fixture(scope="session")
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


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
def patch_get_db_pool_team_service(db_test_pool):
    """Patch the get_db_pool function to return the test pool."""
    with patch("app.services.team_service.get_db_pool", return_value=db_test_pool):
        yield


@pytest.fixture
def patch_get_db_pool_user_service(db_test_pool):
    """Patch the get_db_pool function to return the test pool."""
    with patch("app.services.user_service.get_db_pool", return_value=db_test_pool):
        yield


@pytest.fixture
def patch_get_db_pool_waste_service(db_test_pool):
    """Patch the get_db_pool function to return the test pool."""
    with patch("app.services.waste_service.get_db_pool", return_value=db_test_pool):
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
    with patch("app.services.team_service.TeamRepository", new=FakeTeamRepository) as mock_repo:
        yield mock_repo


fake_team_repo = FakeTeamRepository(None)


@asynccontextmanager
async def get_team_repo() -> AsyncIterator[AbstractTeamRepository]:
    yield fake_team_repo


@pytest.fixture
def get_team_repo_mock():
    with patch("app.services.team_service.get_team_repo", wraps=get_team_repo) as mock_repo:
        yield mock_repo


class FakeUserRepository(AbstractUserRepository):
    def __init__(self, _):
        # In-memory storage for users
        self.users: Dict[int, User] = {}
        self.current_id = 1

    async def create(self, user: User) -> User:
        # Assign a new ID to the user and store it in the dictionary
        user.id = self.current_id
        self.users[self.current_id] = user
        self.current_id += 1
        return user

    async def read(self, user_id: int) -> Optional[User]:
        # Retrieve the user by ID from the dictionary
        return self.users.get(user_id)

    async def delete(self, user_id: int) -> None:
        # Remove the user from the dictionary
        if user_id in self.users:
            del self.users[user_id]

    async def get_users_by_team_id(self, team_id: int) -> List[User]:
        # Filter users by team_id
        return [user for user in self.users.values() if user.team_id == team_id]


fake_user_repo = FakeUserRepository(None)


@asynccontextmanager
async def get_user_repo() -> AsyncIterator[AbstractUserRepository]:
    yield fake_user_repo


@pytest.fixture
def get_user_repo_mock():
    with patch("app.services.user_service.get_user_repo", wraps=get_user_repo) as mock_repo:
        yield mock_repo


class FakeWasteRepository(AbstractWasteRepository):
    def __init__(self, _):
        # In-memory storage for waste entries
        self.entries: Dict[int, WasteEntry] = {}
        self.current_id = 1

    async def create(self, waste_entry: WasteEntry) -> WasteEntry:
        # Assign a new ID to the waste entry and store it in the dictionary
        waste_entry.id = self.current_id
        self.entries[self.current_id] = waste_entry
        self.current_id += 1
        return waste_entry

    async def read(self, entry_id: int) -> Optional[WasteEntry]:
        # Retrieve the waste entry by ID from the dictionary
        return self.entries.get(entry_id)

    async def delete(self, entry_id: int) -> None:
        # Remove the waste entry from the dictionary
        if entry_id in self.entries:
            del self.entries[entry_id]

    async def get_waste_by_user_id(self, user_id: int) -> List[WasteEntry]:
        pass


@asynccontextmanager
async def get_waste_repo() -> AsyncIterator[AbstractWasteRepository]:
    repo = FakeWasteRepository(None)
    yield repo


@pytest.fixture
def get_waste_repo_mock():
    with patch("app.services.waste_service.get_waste_repo", wraps=get_waste_repo) as mock_repo:
        yield mock_repo
