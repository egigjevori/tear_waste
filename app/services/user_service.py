import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator, List, Optional

from app.models.users import User, UserRole
from app.repositories.user_repository import CacheUserRepository, UserRepository
from app.services import team_service
from app.utils.db import get_db_pool

logger = logging.getLogger(__name__)


@asynccontextmanager
async def get_user_repo() -> AsyncIterator[UserRepository]:
    async with get_db_pool().acquire() as conn:
        # yield UserRepository(conn)  # type: ignore
        yield CacheUserRepository(conn)  # type: ignore


async def create_user(
    username: str,
    email: str,
    role: str,
    team_id: int,
    password: str,
) -> User:
    logger.info(f"Creating user with username: {username}, email: {email}, role: {role}, team_id: {team_id}")

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

        logger.info(f"User created with ID: {user.id} and username: {user.username}")
        return user


async def get_user(user_id: int) -> Optional[User]:
    logger.info(f"Fetching user with ID: {user_id}")

    async with get_user_repo() as repo:
        user = await repo.read(user_id)
        return user


async def assert_user_exists(user_id: int) -> None:
    user = await get_user(user_id)
    if not user:
        logger.error(f"User {user_id} does not exist")
        raise ValueError(f"User {user_id} does not exist")


async def delete_user(user_id: int) -> None:
    logger.info(f"Deleting user with ID: {user_id}")

    await assert_user_exists(user_id)
    async with get_user_repo() as repo:
        await repo.delete(user_id)

    logger.info(f"User with ID: {user_id} deleted")


async def get_users_by_team_id(team_id: int) -> List[User]:
    logger.info(f"Fetching users for team ID: {team_id}")

    await team_service.assert_team_exists(team_id=team_id)
    async with get_user_repo() as repo:
        users = await repo.get_users_by_team_id(team_id)

        logger.info(f"Found {len(users)} users for team ID: {team_id}")
        return users


async def get_user_by_username(username: str) -> Optional[User]:
    logger.info(f"Fetching user with username: {username}")

    async with get_user_repo() as repo:
        user = await repo.get_user_by_username(username)

        if user:
            logger.info(f"Found user with ID: {user.id} and username: {user.username}")
        else:
            logger.warning(f"User with username: {username} not found")
        return user
