from app.repositories import Repository

from abc import ABC, abstractmethod
from typing import List, Optional
from app.models.users import User, UserRole


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
        INSERT INTO users (username, email, role, password_hash)
        VALUES ($1, $2, $3, $4)
        RETURNING id
        """
        row = await self.conn.fetchrow(
            query,
            user.username,
            user.email,
            user.role.value,  # Assuming role is an instance of UserRole enum
            user.password_hash
        )
        user.id = row['id']
        return user

    async def read(self, user_id: int) -> Optional[User]:
        query = """
        SELECT *
        FROM users
        WHERE id = $1
        """
        row = await self.conn.fetchrow(query, user_id)
        if row:
            return User(
                id=row['id'],
                username=row['username'],
                email=row['email'],
                role=UserRole(row['role']),
                password_hash=row['password_hash']  # Assuming password_hash is stored directly
            )
        return None
    async def delete(self, user_id: int) -> None:
        query = """
        DELETE FROM users
        WHERE id = $1
        """
        await self.conn.execute(query, user_id)