import os

import asyncpg
from dotenv import load_dotenv

load_dotenv()


DATABASE_URL = (f"postgresql://{os.getenv('POSTGRES_USER')}"
                f":{os.getenv('POSTGRES_PASSWORD')}"
                f"@{os.getenv('POSTGRES_HOST')}"
                f"/{os.getenv('POSTGRES_DB')}")

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
        await conn.execute("""
create table if not exists waste_entries
(
    id        serial
        primary key,
    type      varchar(100)     not null,
    weight    double precision not null,
    timestamp timestamp        not null,
    user_id   integer          not null
);
        """)
