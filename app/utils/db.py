import os

import asyncpg
from asyncpg import UniqueViolationError, ForeignKeyViolationError, PostgresSyntaxError
from dotenv import load_dotenv
from fastapi import HTTPException
from starlette import status

load_dotenv()


DATABASE_URL = (
    f"postgresql://{os.getenv('POSTGRES_USER')}"
    f":{os.getenv('POSTGRES_PASSWORD')}"
    f"@{os.getenv('POSTGRES_HOST')}"
    f"/{os.getenv('POSTGRES_DB')}"
)

pool: asyncpg.Pool


async def connect() -> asyncpg.Pool:
    global pool
    pool = await asyncpg.create_pool(DATABASE_URL)
    return pool


async def disconnect():
    await pool.close()


async def initdb(pool: asyncpg.Pool):
    async with pool.acquire() as conn:
        conn: asyncpg.Connection = conn
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


def get_db_pool() -> asyncpg.pool.Pool:
    return pool


# TODO improve this and handle exceptions somewhere else
# Wrapper function to handle asyncpg exceptions
async def execute_query(conn: asyncpg.Connection, query: str, *args):
    try:
        # Execute the query using asyncpg
        return await conn._execute(query, *args)
    except UniqueViolationError as e:
        # logger.error(f"Unique violation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Unique constraint violated"
        )
    except ForeignKeyViolationError as e:
        # logger.error(f"Foreign key violation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Referenced entity not found"
        )
    except PostgresSyntaxError as e:
        # logger.error(f"SQL Syntax error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="SQL syntax error"
        )
    except Exception as e:
        # logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error occurred",
        )


async def fetchrow(
    conn: asyncpg.Connection,
    query: str,
    *args,
):
    data = await execute_query(conn, query, *args)
    if not data:
        return None
    return data[0]
