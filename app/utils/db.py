import logging
import os
from functools import wraps

import asyncpg
from asyncpg import ForeignKeyViolationError, PostgresSyntaxError, UniqueViolationError
from dotenv import load_dotenv

from app.utils.password import hash_password

logger = logging.getLogger(__name__)
load_dotenv()

DATABASE_URL = (
    f"postgresql://{os.getenv('POSTGRES_USER')}"
    f":{os.getenv('POSTGRES_PASSWORD')}"
    f"@{os.getenv('POSTGRES_HOST')}"
    f":{os.getenv('POSTGRES_PORT')}"
    f"/{os.getenv('POSTGRES_DB')}"
)

pool: asyncpg.Pool


async def connect() -> asyncpg.Pool:
    global pool
    logger.info("Connecting to the database")
    pool = await asyncpg.create_pool(DATABASE_URL)
    logger.info("Database connection pool created")
    return pool


async def disconnect():
    global pool
    logger.info("Closing the database connection pool")
    await pool.close()
    logger.info("Database connection pool closed")


async def initdb(pool: asyncpg.Pool):
    logger.info("Initializing the database")
    async with pool.acquire() as conn:
        logger.info("Creating tables")
        await conn.execute(
            """
            create table if not exists waste_entries
            (
                id        serial
                    primary key,
                type      varchar(100)     not null,
                weight    double precision not null,
                timestamp timestamp        not null,
                user_id   integer          not null
            );
        """
        )
        await conn.execute(
            """
            create table if not exists users
            (
                id            serial primary key,
                username      varchar(150) not null unique,
                email         varchar(255) not null unique,
                role          varchar(60)  not null,
                team_id   integer          not null,
                password_hash varchar(60)  not null
            );
        """
        )
        await conn.execute(
            """
            create table if not exists teams
            (
                id         serial primary key,
                name       varchar(100) not null unique
            );
        """
        )
        logger.info("Creating indexes")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_waste_entries_user_id ON waste_entries (user_id);")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_users_team_id ON users (team_id);")
        await conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_username ON users (username);")
        await conn.execute(
            """
            INSERT INTO teams (name)
            SELECT 'Admin'
            WHERE NOT EXISTS (
                SELECT 1 FROM teams WHERE name = 'Admin'
            );
        """
        )
        existing_user = await conn.fetchrow(
            """
            SELECT id FROM users WHERE username = $1
            """,
            "admin",
        )
        if not existing_user:
            _ = await conn.fetchval(
                """
                INSERT INTO users (username, email, role, password_hash, team_id)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING id
                """,
                "admin",
                "admin@example.com",
                "Admin",
                hash_password("admin"),
                1,
            )
            logger.info("Inserted new admin user")
    logger.info("Database initialized")


def get_db_pool() -> asyncpg.pool.Pool:
    global pool
    return pool


class DatabaseError(Exception):
    pass


def handle_errors(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            result = await func(*args, **kwargs)
        except UniqueViolationError as e:
            logger.error(f"Unique violation error: {str(e)}")
            raise DatabaseError("Unique constraint violated")
        except ForeignKeyViolationError as e:
            logger.error(f"Foreign key violation error: {str(e)}")
            raise DatabaseError("Referenced entity not found")
        except PostgresSyntaxError as e:
            logger.error(f"SQL Syntax error: {str(e)}")
            raise DatabaseError("SQL syntax error")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise DatabaseError("Unexpected error occurred")

        return result

    return wrapper


@handle_errors
async def execute(conn: asyncpg.Connection, query: str, *args):
    logger.info(f"Executing query: {query}")
    return await conn.execute(query, *args)


@handle_errors
async def fetchrow(
    conn: asyncpg.Connection,
    query: str,
    *args,
):
    logger.info(f"Fetching row with query: {query}")
    data = await conn.fetchrow(query, *args)
    return data


@handle_errors
async def fetch(
    conn: asyncpg.Connection,
    query: str,
    *args,
):
    logger.info(f"Fetching data with query: {query}")
    data = await conn.fetch(query, *args)
    return data
