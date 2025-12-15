"""Telemetry database queries."""

from datetime import datetime
from uuid import UUID

import asyncpg

from src.core.database import fetch, fetchrow, fetchval, execute, get_connection


async def insert_telemetry(
    time: datetime,
    station_id: UUID,
    device_id: UUID,
    metric_type: str,
    value: float,
    unit: str | None = None,
    quality: int = 100,
    metadata: dict | None = None,
) -> None:
    """Insert a single telemetry record."""
    await execute(
        """
        INSERT INTO telemetry (time, station_id, device_id, metric_type, value, unit, quality, metadata)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        """,
        time,
        station_id,
        device_id,
        metric_type,
        value,
        unit,
        quality,
        metadata or {},
    )


async def insert_telemetry_batch(records: list[dict]) -> None:
    """Insert multiple telemetry records in a batch."""
    async with get_connection() as conn:
        await conn.executemany(
            """
            INSERT INTO telemetry (time, station_id, device_id, metric_type, value, unit, quality, metadata)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """,
            [
                (
                    r["time"],
                    r["station_id"],
                    r["device_id"],
                    r["metric_type"],
                    r["value"],
                    r.get("unit"),
                    r.get("quality", 100),
                    r.get("metadata", {}),
                )
                for r in records
            ],
        )


async def get_telemetry(
    station_id: UUID | None = None,
    device_id: UUID | None = None,
    metric_type: str | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[asyncpg.Record]:
    """Query telemetry data with filters."""
    conditions = []
    params = []
    param_idx = 1

    if station_id is not None:
        conditions.append(f"station_id = ${param_idx}")
        params.append(station_id)
        param_idx += 1

    if device_id is not None:
        conditions.append(f"device_id = ${param_idx}")
        params.append(device_id)
        param_idx += 1

    if metric_type is not None:
        conditions.append(f"metric_type = ${param_idx}")
        params.append(metric_type)
        param_idx += 1

    if start_time is not None:
        conditions.append(f"time >= ${param_idx}")
        params.append(start_time)
        param_idx += 1

    if end_time is not None:
        conditions.append(f"time <= ${param_idx}")
        params.append(end_time)
        param_idx += 1

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    params.extend([limit, offset])
    query = f"""
        SELECT time, station_id, device_id, metric_type, value, unit, quality
        FROM telemetry
        {where_clause}
        ORDER BY time DESC
        LIMIT ${param_idx} OFFSET ${param_idx + 1}
    """
    return await fetch(query, *params)


async def get_telemetry_aggregates(
    station_id: UUID,
    metric_type: str,
    start_time: datetime,
    end_time: datetime,
    interval: str = "1 hour",
) -> list[asyncpg.Record]:
    """Get aggregated telemetry data."""
    return await fetch(
        f"""
        SELECT
            date_trunc('hour', time) as bucket,
            station_id,
            metric_type,
            AVG(value) as avg_value,
            MIN(value) as min_value,
            MAX(value) as max_value,
            COUNT(*) as sample_count
        FROM telemetry
        WHERE station_id = $1
          AND metric_type = $2
          AND time >= $3
          AND time <= $4
        GROUP BY bucket, station_id, metric_type
        ORDER BY bucket DESC
        """,
        station_id,
        metric_type,
        start_time,
        end_time,
    )


async def get_latest_telemetry(station_id: UUID) -> list[asyncpg.Record]:
    """Get the latest telemetry value for each metric type."""
    return await fetch(
        """
        SELECT DISTINCT ON (metric_type)
            time, station_id, metric_type, value, unit
        FROM telemetry
        WHERE station_id = $1
        ORDER BY metric_type, time DESC
        """,
        station_id,
    )


async def get_device_by_id(device_id: UUID) -> asyncpg.Record | None:
    """Get a device by ID."""
    return await fetchrow(
        """
        SELECT id, station_id, device_type, model, serial_number,
               firmware_version, last_seen_at, status, config, created_at, updated_at
        FROM devices
        WHERE id = $1
        """,
        device_id,
    )


async def get_devices_by_station(station_id: UUID) -> list[asyncpg.Record]:
    """Get all devices for a station."""
    return await fetch(
        """
        SELECT id, station_id, device_type, model, serial_number,
               firmware_version, last_seen_at, status, config, created_at
        FROM devices
        WHERE station_id = $1
        ORDER BY device_type, created_at
        """,
        station_id,
    )


async def create_device(
    station_id: UUID,
    device_type: str,
    model: str | None = None,
    serial_number: str | None = None,
    firmware_version: str | None = None,
    config: dict | None = None,
) -> asyncpg.Record:
    """Create a new device."""
    return await fetchrow(
        """
        INSERT INTO devices (station_id, device_type, model, serial_number, firmware_version, config)
        VALUES ($1, $2, $3, $4, $5, $6)
        RETURNING id, station_id, device_type, model, serial_number,
                  firmware_version, last_seen_at, status, config, created_at, updated_at
        """,
        station_id,
        device_type,
        model,
        serial_number,
        firmware_version,
        config or {},
    )


async def update_device_status(device_id: UUID, status: str) -> bool:
    """Update device status."""
    result = await execute(
        """
        UPDATE devices
        SET status = $1, last_seen_at = NOW()
        WHERE id = $2
        """,
        status,
        device_id,
    )
    return result == "UPDATE 1"


async def get_or_create_gateway(station_id: UUID) -> asyncpg.Record:
    """Get or create the gateway device for a station."""
    device = await fetchrow(
        """
        SELECT id, station_id, device_type, model, serial_number,
               firmware_version, last_seen_at, status, config, created_at
        FROM devices
        WHERE station_id = $1 AND device_type = 'gateway'
        """,
        station_id,
    )
    if device:
        return device
    return await create_device(station_id, "gateway")
