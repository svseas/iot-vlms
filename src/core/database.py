"""AsyncPG database connection pool management."""

import json
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import asyncpg

from src.core.config import get_settings

logger = logging.getLogger(__name__)

_pool: asyncpg.Pool | None = None


async def _init_connection(conn: asyncpg.Connection) -> None:
    """Initialize connection with custom type codecs."""
    await conn.set_type_codec(
        "jsonb",
        encoder=json.dumps,
        decoder=json.loads,
        schema="pg_catalog",
    )
    await conn.set_type_codec(
        "json",
        encoder=json.dumps,
        decoder=json.loads,
        schema="pg_catalog",
    )


async def create_pool() -> asyncpg.Pool:
    """Create and return a new connection pool."""
    settings = get_settings()
    pool = await asyncpg.create_pool(
        dsn=settings.database_url,
        min_size=5,
        max_size=20,
        command_timeout=60,
        init=_init_connection,
    )
    logger.info("Database connection pool created")
    return pool


async def get_pool() -> asyncpg.Pool:
    """Get the existing connection pool or create a new one."""
    global _pool
    if _pool is None:
        _pool = await create_pool()
    return _pool


async def close_pool() -> None:
    """Close the connection pool."""
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None
        logger.info("Database connection pool closed")


@asynccontextmanager
async def get_connection() -> AsyncGenerator[asyncpg.Connection, None]:
    """Get a connection from the pool."""
    pool = await get_pool()
    async with pool.acquire() as connection:
        yield connection


@asynccontextmanager
async def get_transaction() -> AsyncGenerator[asyncpg.Connection, None]:
    """Get a connection with an active transaction."""
    pool = await get_pool()
    async with pool.acquire() as connection:
        async with connection.transaction():
            yield connection


async def execute(query: str, *args) -> str:
    """Execute a query and return the status."""
    async with get_connection() as conn:
        return await conn.execute(query, *args)


async def fetch(query: str, *args) -> list[asyncpg.Record]:
    """Execute a query and return all rows."""
    async with get_connection() as conn:
        return await conn.fetch(query, *args)


async def fetchrow(query: str, *args) -> asyncpg.Record | None:
    """Execute a query and return a single row."""
    async with get_connection() as conn:
        return await conn.fetchrow(query, *args)


async def fetchval(query: str, *args):
    """Execute a query and return a single value."""
    async with get_connection() as conn:
        return await conn.fetchval(query, *args)
