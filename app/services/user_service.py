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
    # TODO check if team exists
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
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        return user


async def delete_user(user_id: int) -> None:
    user = await get_user(user_id)
    if not user:
        raise ValueError(f"User with ID {user_id} not found")

    async with get_user_repo() as repo:
        await repo.delete(user_id)


async def get_users_by_team_id(team_id: int) -> List[User]:
    if team_service.team_exists(team_id=team_id):
        async with get_user_repo() as repo:
            users = await repo.get_users_by_team_id(team_id)
            return users
    else:
        raise ValueError(f"Team with ID {team_id} not found")
