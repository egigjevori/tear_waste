from abc import ABC, abstractmethod
from typing import List, Optional

from app.models.users import User, UserRole
from app.repositories import Repository
from app.utils.db import execute_query, fetchrow


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
            return User(
                id=row["id"],
                username=row["username"],
                email=row["email"],
                team_id=row["team_id"],
                role=UserRole(row["role"]),
                password_hash=row[
                    "password_hash"
                ],  # Assuming password_hash is stored directly
            )
        return None

    async def delete(self, user_id: int) -> None:
        query = """
        DELETE FROM users
        WHERE id = $1
        """
        await execute_query(self.conn, query, user_id)
