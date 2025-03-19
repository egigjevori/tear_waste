import logging
import os
from functools import wraps

import asyncpg
from asyncpg import (ForeignKeyViolationError, PostgresSyntaxError,
                     UniqueViolationError)
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


def handle_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except UniqueViolationError as _:
            # logger.error(f"Unique violation error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Unique constraint violated"
            )
        except ForeignKeyViolationError as _:
            # logger.error(f"Foreign key violation error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Referenced entity not found"
            )
        except PostgresSyntaxError as _:
            # logger.error(f"SQL Syntax error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="SQL syntax error"
            )
        except Exception as _:
            # logger.error(f"Unexpected error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unexpected error occurred",
            )

        return result
    return wrapper

@handle_errors
async def execute(conn: asyncpg.Connection, query: str, *args):
    logging.info(query)
    return await conn.execute(query, *args)

@handle_errors
async def fetchrow(
    conn: asyncpg.Connection,
    query: str,
    *args,
):
    logging.info(query)
    data = await conn.fetchrow(query, *args)
    if not data:
        return None
    return data[0]
