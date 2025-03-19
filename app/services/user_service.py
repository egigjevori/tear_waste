from contextlib import asynccontextmanager
from typing import AsyncIterator, Optional, List

from app.models.users import User, UserRole
from app.repositories.user_repository import UserRepository
from app.services import team_service
from app.utils.db import get_db_pool


@asynccontextmanager
async def get_user_repo() -> AsyncIterator[UserRepository]:
    async with get_db_pool().acquire() as conn:
        yield UserRepository(conn)  # type: ignore


async def create_user(
    username: str,
    email: str,
    role: str,
    team_id: int,
    password: str,
) -> User:
    # TODO validate data
    await team_service.assert_team_exists(team_id=team_id)
    user = User(
        username=username,
        email=email,
        role=UserRole(role),
        team_id=team_id,
    )
    user.set_password(password)

    async with get_user_repo() as repo:
        user = await repo.create(user)
        return user


async def get_user(user_id: int) -> Optional[User]:
    async with get_user_repo() as repo:
        user = await repo.read(user_id)
        return user

async def assert_user_exists(user_id: int) -> None:
    user = await get_user(user_id)
    if not user:
        raise ValueError(f"User {user_id} does not exist")

async def delete_user(user_id: int) -> None:
    await assert_user_exists(user_id)
    async with get_user_repo() as repo:
        await repo.delete(user_id)

async def get_users_by_team_id(team_id: int) -> List[User]:
    await team_service.assert_team_exists(team_id=team_id)
    async with get_user_repo() as repo:
        users = await repo.get_users_by_team_id(team_id)
        return users

