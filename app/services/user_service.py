from contextlib import asynccontextmanager
from typing import AsyncIterator

from app.models.users import User, UserRole
from app.repositories.user_repository import UserRepository
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
