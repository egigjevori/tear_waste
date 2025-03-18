import asyncpg
import pytest

from app.models.users import User, UserRole
from app.repositories.user_repository import UserRepository


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


@pytest.mark.asyncio
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


@pytest.mark.asyncio
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


@pytest.mark.asyncio
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
