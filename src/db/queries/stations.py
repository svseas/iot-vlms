"""Station database queries."""

from uuid import UUID

import asyncpg

from src.core.database import fetch, fetchrow, fetchval, execute


async def get_station_by_id(station_id: UUID) -> asyncpg.Record | None:
    """Get a station by ID."""
    return await fetchrow(
        """
        SELECT id, code, name,
               ST_Y(location::geometry) as lat,
               ST_X(location::geometry) as lng,
               region_id, status, commissioned_at, metadata, created_at, updated_at
        FROM stations
        WHERE id = $1
        """,
        station_id,
    )


async def get_station_by_code(code: str) -> asyncpg.Record | None:
    """Get a station by code."""
    return await fetchrow(
        """
        SELECT id, code, name,
               ST_Y(location::geometry) as lat,
               ST_X(location::geometry) as lng,
               region_id, status, commissioned_at, metadata, created_at, updated_at
        FROM stations
        WHERE code = $1
        """,
        code,
    )


async def create_station(
    code: str,
    name: str,
    lat: float,
    lng: float,
    region_id: UUID | None = None,
    metadata: dict | None = None,
) -> asyncpg.Record:
    """Create a new station."""
    return await fetchrow(
        """
        INSERT INTO stations (code, name, location, region_id, metadata)
        VALUES ($1, $2, ST_SetSRID(ST_MakePoint($4, $3), 4326), $5, $6)
        RETURNING id, code, name,
                  ST_Y(location::geometry) as lat,
                  ST_X(location::geometry) as lng,
                  region_id, status, commissioned_at, metadata, created_at, updated_at
        """,
        code,
        name,
        lat,
        lng,
        region_id,
        metadata or {},
    )


async def update_station(
    station_id: UUID,
    name: str | None = None,
    lat: float | None = None,
    lng: float | None = None,
    region_id: UUID | None = None,
    status: str | None = None,
    metadata: dict | None = None,
) -> asyncpg.Record | None:
    """Update a station."""
    updates = []
    params = []
    param_idx = 1

    if name is not None:
        updates.append(f"name = ${param_idx}")
        params.append(name)
        param_idx += 1

    if lat is not None and lng is not None:
        updates.append(f"location = ST_SetSRID(ST_MakePoint(${param_idx + 1}, ${param_idx}), 4326)")
        params.extend([lat, lng])
        param_idx += 2

    if region_id is not None:
        updates.append(f"region_id = ${param_idx}")
        params.append(region_id)
        param_idx += 1

    if status is not None:
        updates.append(f"status = ${param_idx}")
        params.append(status)
        param_idx += 1

    if metadata is not None:
        updates.append(f"metadata = ${param_idx}")
        params.append(metadata)
        param_idx += 1

    if not updates:
        return await get_station_by_id(station_id)

    params.append(station_id)
    query = f"""
        UPDATE stations
        SET {", ".join(updates)}
        WHERE id = ${param_idx}
        RETURNING id, code, name,
                  ST_Y(location::geometry) as lat,
                  ST_X(location::geometry) as lng,
                  region_id, status, commissioned_at, metadata, created_at, updated_at
    """
    return await fetchrow(query, *params)


async def delete_station(station_id: UUID) -> bool:
    """Delete a station."""
    result = await execute(
        "DELETE FROM stations WHERE id = $1",
        station_id,
    )
    return result == "DELETE 1"


async def list_stations(
    limit: int = 20,
    offset: int = 0,
    status: str | None = None,
    region_id: UUID | None = None,
    search: str | None = None,
) -> list[asyncpg.Record]:
    """List stations with optional filters."""
    conditions = []
    params = []
    param_idx = 1

    if status is not None:
        conditions.append(f"status = ${param_idx}")
        params.append(status)
        param_idx += 1

    if region_id is not None:
        conditions.append(f"region_id = ${param_idx}")
        params.append(region_id)
        param_idx += 1

    if search is not None:
        conditions.append(f"(name ILIKE ${param_idx} OR code ILIKE ${param_idx})")
        params.append(f"%{search}%")
        param_idx += 1

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    params.extend([limit, offset])
    query = f"""
        SELECT id, code, name,
               ST_Y(location::geometry) as lat,
               ST_X(location::geometry) as lng,
               region_id, status, created_at
        FROM stations
        {where_clause}
        ORDER BY created_at DESC
        LIMIT ${param_idx} OFFSET ${param_idx + 1}
    """
    return await fetch(query, *params)


async def count_stations(
    status: str | None = None,
    region_id: UUID | None = None,
    search: str | None = None,
) -> int:
    """Count stations with optional filters."""
    conditions = []
    params = []
    param_idx = 1

    if status is not None:
        conditions.append(f"status = ${param_idx}")
        params.append(status)
        param_idx += 1

    if region_id is not None:
        conditions.append(f"region_id = ${param_idx}")
        params.append(region_id)
        param_idx += 1

    if search is not None:
        conditions.append(f"(name ILIKE ${param_idx} OR code ILIKE ${param_idx})")
        params.append(f"%{search}%")
        param_idx += 1

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    query = f"SELECT COUNT(*) FROM stations {where_clause}"
    return await fetchval(query, *params)


async def check_code_exists(code: str, exclude_station_id: UUID | None = None) -> bool:
    """Check if station code is already in use."""
    if exclude_station_id:
        return await fetchval(
            "SELECT EXISTS(SELECT 1 FROM stations WHERE code = $1 AND id != $2)",
            code,
            exclude_station_id,
        )
    return await fetchval(
        "SELECT EXISTS(SELECT 1 FROM stations WHERE code = $1)",
        code,
    )


async def get_stations_by_region(region_id: UUID) -> list[asyncpg.Record]:
    """Get all stations in a region."""
    return await fetch(
        """
        SELECT id, code, name,
               ST_Y(location::geometry) as lat,
               ST_X(location::geometry) as lng,
               status, created_at
        FROM stations
        WHERE region_id = $1
        ORDER BY name
        """,
        region_id,
    )
