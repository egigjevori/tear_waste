from abc import abstractmethod
from typing import List, Optional

from app.models.users import User, UserRole
from app.repositories import Repository
from app.utils import cache
from app.utils.cache import set_value
from app.utils.db import execute, fetch, fetchrow


class AbstractUserRepository(Repository):
    @abstractmethod
    async def create(self, user: User) -> User:
        """Create a new user."""
        raise NotImplementedError

    @abstractmethod
    async def read(self, user_id: int) -> Optional[User]:
        """Read a user by their ID."""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, user_id: int) -> None:
        """Delete a user by their ID."""
        raise NotImplementedError

    @abstractmethod
    async def get_users_by_team_id(self, team_id: int) -> List[User]:
        """Get users by their team id."""
        raise NotImplementedError

    @abstractmethod
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get users by their team id."""
        raise NotImplementedError


class UserRepository(AbstractUserRepository):

    async def create(self, user: User) -> User:
        query = """
        INSERT INTO users (username, email, role, password_hash, team_id)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING id
        """
        row = await fetchrow(
            self.conn,
            query,
            user.username,
            user.email,
            user.role.value,  # Assuming role is an instance of UserRole enum
            user.password_hash,
            user.team_id,
        )
        user.id = row["id"]
        return user

    async def read(self, user_id: int) -> Optional[User]:
        query = """
        SELECT *
        FROM users
        WHERE id = $1
        """
        row = await fetchrow(self.conn, query, user_id)
        if row:
            return User.from_dict(row)
        return None

    async def delete(self, user_id: int) -> None:
        query = """
        DELETE FROM users
        WHERE id = $1
        """
        await execute(self.conn, query, user_id)

    async def get_users_by_team_id(self, team_id: int) -> List[User]:
        query = """
        SELECT *
        FROM users
        WHERE team_id = $1
        """
        rows = await fetch(self.conn, query, team_id)
        users = [
            User.from_dict(row)
            for row in rows
        ]
        return users

    async def get_user_by_username(self, username: str) -> Optional[User]:
        query = """
        SELECT *
        FROM users
        WHERE username = $1
        """
        row = await fetchrow(self.conn, query, username)
        if row:
            return User.from_dict(row)
        return None

class CacheUserRepository(UserRepository):
    async def create(self, user: User) -> User:
        result = await super().create(user)
        await set_value(f"user:{result.id}", result.to_dict())
        return result

    async def read(self, user_id: int) -> Optional[User]:
        cache_key = f"user:{user_id}"
        cached_data = await cache.get_value(cache_key)
        if cached_data is not None:
            return User.from_dict(cached_data)
        else:
            result = await super().read(user_id)
            if result:
                await set_value(cache_key, result.to_dict())
            return result

    async def delete(self, user_id: int) -> None:
        user = await self.read(user_id)
        await super().delete(user.id)
        await cache.delete_key(f"user:{user.id}")
        await cache.delete_key(f"users_by_team_id:{user.team_id}")
        await cache.delete_key(f"users_by_username:{user.username}")

    async def get_users_by_team_id(self, team_id: int) -> List[User]:
        cache_key = f"users_by_team_id:{team_id}"
        cached_data = await cache.get_value(cache_key)
        if cached_data is not None:
            return [User.from_dict(data) for data in cached_data]
        else:
            results = await super().get_users_by_team_id(team_id)
            if results:
                await set_value(cache_key, [result.to_dict() for result in results])
            return results

    async def get_user_by_username(self, username: str) -> Optional[User]:
        cache_key = f"user_by_username:{username}"
        cached_data = await cache.get_value(cache_key)
        if cached_data is not None:
            return User.from_dict(cached_data)
        else:
            result = await super().get_user_by_username(username)
            if result:
                await set_value(cache_key, result.to_dict())
            return result
