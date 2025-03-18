import asyncpg
from app.models.users import User, UserRole
from app.repositories.user_repository import UserRepository

async def test_create_user(db_test_pool: asyncpg.Pool):
    # Arrange
    async with db_test_pool.acquire() as conn:
        repo = UserRepository(conn)
        user = User(
            username='johndoe',
            email='johndoe@example.com',
            role=UserRole.EMPLOYEE,
        )
        user.set_password('securepassword123')

        # Act
        created_user = await repo.create(user)

        # Assert
        assert created_user.id is not None

        # Verify the user exists in the database
        row = await conn.fetchrow("SELECT * FROM users WHERE id = $1", created_user.id)
        assert row is not None
        assert row['username'] == 'johndoe'
        assert row['email'] == 'johndoe@example.com'
        assert row['role'] == UserRole.EMPLOYEE.value
        assert row['password_hash'] == created_user.password_hash

async def test_read_user(db_test_pool: asyncpg.Pool):
    # Arrange
    async with db_test_pool.acquire() as conn:
        repo = UserRepository(conn)
        user = User(
            username='janedoe',
            email='janedoe@example.com',
            role=UserRole.MANAGER,
        )
        user.set_password('securepassword456')

        # Create a user to read
        created_user = await repo.create(user)

        # Act
        read_user = await repo.read(created_user.id)

        # Assert
        assert read_user is not None
        assert read_user.id == created_user.id
        assert read_user.username == 'janedoe'
        assert read_user.email == 'janedoe@example.com'
        assert read_user.role == UserRole.MANAGER
        assert read_user.password_hash == created_user.password_hash

        read_user = await repo.read(2)
        assert read_user is None

async def test_delete_user(db_test_pool: asyncpg.Pool):
    # Arrange
    async with db_test_pool.acquire() as conn:
        repo = UserRepository(conn)
        user = User(
            username='janedoe',
            email='janedoe@example.com',
            role=UserRole.MANAGER,
        )
        user.set_password('securepassword456')

        # Create a user to delete
        created_user = await repo.create(user)

        # Act
        await repo.delete(created_user.id)

        # Assert
        # Verify the user no longer exists in the database
        row = await conn.fetchrow("SELECT * FROM users WHERE id = $1", created_user.id)
        assert row is None
