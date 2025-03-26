from __future__ import annotations

import json
import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncIterator

import redis.asyncio as redis
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()

HOST = os.getenv('REDIS_HOST')
PORT = os.getenv('REDIS_PORT')
DB = os.getenv('REDIS_DB')


pool = redis.ConnectionPool(host=HOST, port=PORT, db=DB, protocol=3)

@asynccontextmanager
async def get_cache() -> AsyncIterator[redis.Redis]:
    async with redis.Redis(connection_pool=pool) as cache:
        cache: redis.Redis = cache
        yield cache


async def set_value(key: str, value: dict | list[dict]):
    async with get_cache() as cache:
        # Serialize the dictionary to a JSON string
        json_value = json.dumps(value)
        await cache.set(key, json_value.encode('utf-8'))


async def get_value(key: str) -> dict | list[dict] | None:
    async with get_cache() as cache:
        value = await cache.get(key)
        if value is not None:
            # Deserialize the JSON string back to a dictionary
            return json.loads(value.decode('utf-8'))
        return None

async def delete_key(key: str):
    async with get_cache() as cache:
        await cache.delete(key)
