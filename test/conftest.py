# conftest.py

import os
import pytest
import asyncpg
from dotenv import load_dotenv

from app.utils.db import initdb

# Load environment variables from a .env file
load_dotenv(dotenv_path=".env.test")


async def drop_tables(pool: asyncpg.Pool):
    async with pool.acquire() as conn:
        conn: asyncpg.Connection = conn
        for table in ["waste_entries", "users", "teams"]:
            await conn.execute(f"drop table if exists {table}; ")



@pytest.fixture
async def db_test_pool():
    """Create an asyncpg connection pool."""
    pool = await asyncpg.create_pool(
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        database=os.getenv("POSTGRES_DB"),
        host=os.getenv("POSTGRES_HOST"),
        min_size=1,  # Minimum number of connections in the pool
        max_size=10  # Maximum number of connections in the pool
    )
    await initdb(pool)
    yield pool
    await drop_tables(pool)
    await pool.close()