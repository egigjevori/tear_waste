import asyncpg
import pytest

from app.models.users import User, UserRole
from app.repositories.user_repository import CacheUserRepository, UserRepository


def create_test_user() -> User:
    """Utility function to create a User object with predefined data for testing."""
    user = User(
        username="testuser",
        email="testuser@example.com",
        role=UserRole.EMPLOYEE,
        team_id=1,
    )
    user.set_password("testpassword123")
    return user


async def test_create_user(db_test_pool: asyncpg.Pool):
    # Arrange
    async with db_test_pool.acquire() as conn:
        repo = UserRepository(conn)
        user = create_test_user()

        # Act
        created_user = await repo.create(user)

        # Assert
        assert created_user.id is not None

        # Verify the user exists in the database
        row = await conn.fetchrow("SELECT * FROM users WHERE id = $1", created_user.id)
        assert row is not None
        assert row["username"] == "testuser"
        assert row["email"] == "testuser@example.com"
        assert row["role"] == UserRole.EMPLOYEE.value
        assert row["password_hash"] == created_user.password_hash
        assert row["team_id"] == created_user.team_id


async def test_read_user(db_test_pool: asyncpg.Pool):
    # Arrange
    async with db_test_pool.acquire() as conn:
        repo = UserRepository(conn)
        user = create_test_user()

        # Create a user to read
        created_user = await repo.create(user)

        # Act
        read_user = await repo.read(created_user.id)

        # Assert
        assert read_user is not None
        assert read_user.id == created_user.id
        assert read_user.username == "testuser"
        assert read_user.email == "testuser@example.com"
        assert read_user.role == UserRole.EMPLOYEE
        assert read_user.password_hash == created_user.password_hash
        assert read_user.team_id == created_user.team_id

        # Test reading a non-existent user
        read_user = await repo.read(9999)  # Assuming 9999 is a non-existent ID
        assert read_user is None


async def test_delete_user(db_test_pool: asyncpg.Pool):
    # Arrange
    async with db_test_pool.acquire() as conn:
        repo = UserRepository(conn)
        user = create_test_user()

        # Create a user to delete
        created_user = await repo.create(user)

        # Act
        await repo.delete(created_user.id)

        # Assert
        # Verify the user no longer exists in the database
        row = await conn.fetchrow("SELECT * FROM users WHERE id = $1", created_user.id)
        assert row is None


async def test_get_users_by_team_id(db_test_pool: asyncpg.Pool):
    # Arrange
    async with db_test_pool.acquire() as conn:
        repo = UserRepository(conn)

        # Create multiple users with the same team_id
        user1 = create_test_user()
        user2 = create_test_user()
        user2.username = "testuser2"
        user2.email = "testuser2@example.com"

        created_user1 = await repo.create(user1)
        created_user2 = await repo.create(user2)

        # Act
        users = await repo.get_users_by_team_id(user1.team_id)

        # Assert
        assert len(users) == 3
        assert any(u.id == created_user1.id for u in users)
        assert any(u.id == created_user2.id for u in users)

        # Test with a team_id that has no users
        users = await repo.get_users_by_team_id(9999)  # Assuming 9999 is a non-existent team_id
        assert len(users) == 0


async def test_get_users_by_team_id_cache(db_test_pool: asyncpg.Pool):
    # Arrange
    async with db_test_pool.acquire() as conn:
        repo = CacheUserRepository(conn)

        # Create multiple users with the same team_id
        user1 = create_test_user()
        user2 = create_test_user()
        user2.username = "testuser2"
        user2.email = "testuser2@example.com"

        created_user1 = await repo.create(user1)
        created_user2 = await repo.create(user2)

        # Act
        users = await repo.get_users_by_team_id(user1.team_id)
        users = await repo.get_users_by_team_id(user1.team_id)
        users = await repo.get_users_by_team_id(user1.team_id)

        await repo.delete(created_user1.id)

        users = await repo.get_users_by_team_id(user2.team_id)

        # Assert
        assert len(users) == 2
        assert any(u.id == created_user2.id for u in users)
