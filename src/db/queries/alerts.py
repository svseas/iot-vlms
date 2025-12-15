"""Alert database queries."""

from datetime import datetime
from uuid import UUID

import asyncpg

from src.core.database import fetch, fetchrow, fetchval, execute


async def get_alert_by_id(alert_id: UUID) -> asyncpg.Record | None:
    """Get an alert by ID."""
    return await fetchrow(
        """
        SELECT a.id, a.station_id, a.alert_type, a.severity, a.title, a.message,
               a.acknowledged_at, a.acknowledged_by, a.resolved_at, a.metadata, a.created_at,
               s.name as station_name
        FROM alerts a
        LEFT JOIN stations s ON a.station_id = s.id
        WHERE a.id = $1
        """,
        alert_id,
    )


async def create_alert(
    station_id: UUID,
    alert_type: str,
    severity: str,
    title: str,
    message: str | None = None,
    metadata: dict | None = None,
) -> asyncpg.Record:
    """Create a new alert."""
    return await fetchrow(
        """
        INSERT INTO alerts (station_id, alert_type, severity, title, message, metadata)
        VALUES ($1, $2, $3, $4, $5, $6)
        RETURNING id, station_id, alert_type, severity, title, message,
                  acknowledged_at, acknowledged_by, resolved_at, metadata, created_at
        """,
        station_id,
        alert_type,
        severity,
        title,
        message,
        metadata or {},
    )


async def acknowledge_alert(alert_id: UUID, user_id: UUID) -> asyncpg.Record | None:
    """Acknowledge an alert."""
    return await fetchrow(
        """
        UPDATE alerts
        SET acknowledged_at = NOW(), acknowledged_by = $2
        WHERE id = $1 AND acknowledged_at IS NULL
        RETURNING id, station_id, alert_type, severity, title, message,
                  acknowledged_at, acknowledged_by, resolved_at, metadata, created_at
        """,
        alert_id,
        user_id,
    )


async def resolve_alert(alert_id: UUID) -> asyncpg.Record | None:
    """Resolve an alert."""
    return await fetchrow(
        """
        UPDATE alerts
        SET resolved_at = NOW()
        WHERE id = $1 AND resolved_at IS NULL
        RETURNING id, station_id, alert_type, severity, title, message,
                  acknowledged_at, acknowledged_by, resolved_at, metadata, created_at
        """,
        alert_id,
    )


async def list_alerts(
    station_id: UUID | None = None,
    alert_type: str | None = None,
    severity: str | None = None,
    acknowledged: bool | None = None,
    resolved: bool | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[asyncpg.Record]:
    """List alerts with optional filters."""
    conditions = []
    params = []
    param_idx = 1

    if station_id is not None:
        conditions.append(f"a.station_id = ${param_idx}")
        params.append(station_id)
        param_idx += 1

    if alert_type is not None:
        conditions.append(f"a.alert_type = ${param_idx}")
        params.append(alert_type)
        param_idx += 1

    if severity is not None:
        conditions.append(f"a.severity = ${param_idx}")
        params.append(severity)
        param_idx += 1

    if acknowledged is not None:
        if acknowledged:
            conditions.append("a.acknowledged_at IS NOT NULL")
        else:
            conditions.append("a.acknowledged_at IS NULL")

    if resolved is not None:
        if resolved:
            conditions.append("a.resolved_at IS NOT NULL")
        else:
            conditions.append("a.resolved_at IS NULL")

    if start_date is not None:
        conditions.append(f"a.created_at >= ${param_idx}")
        params.append(start_date)
        param_idx += 1

    if end_date is not None:
        conditions.append(f"a.created_at <= ${param_idx}")
        params.append(end_date)
        param_idx += 1

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    params.extend([limit, offset])
    query = f"""
        SELECT a.id, a.station_id, s.name as station_name, a.alert_type, a.severity,
               a.title, a.acknowledged_at, a.resolved_at, a.created_at
        FROM alerts a
        LEFT JOIN stations s ON a.station_id = s.id
        {where_clause}
        ORDER BY a.created_at DESC
        LIMIT ${param_idx} OFFSET ${param_idx + 1}
    """
    return await fetch(query, *params)


async def count_alerts(
    station_id: UUID | None = None,
    alert_type: str | None = None,
    severity: str | None = None,
    acknowledged: bool | None = None,
    resolved: bool | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> int:
    """Count alerts with optional filters."""
    conditions = []
    params = []
    param_idx = 1

    if station_id is not None:
        conditions.append(f"station_id = ${param_idx}")
        params.append(station_id)
        param_idx += 1

    if alert_type is not None:
        conditions.append(f"alert_type = ${param_idx}")
        params.append(alert_type)
        param_idx += 1

    if severity is not None:
        conditions.append(f"severity = ${param_idx}")
        params.append(severity)
        param_idx += 1

    if acknowledged is not None:
        if acknowledged:
            conditions.append("acknowledged_at IS NOT NULL")
        else:
            conditions.append("acknowledged_at IS NULL")

    if resolved is not None:
        if resolved:
            conditions.append("resolved_at IS NOT NULL")
        else:
            conditions.append("resolved_at IS NULL")

    if start_date is not None:
        conditions.append(f"created_at >= ${param_idx}")
        params.append(start_date)
        param_idx += 1

    if end_date is not None:
        conditions.append(f"created_at <= ${param_idx}")
        params.append(end_date)
        param_idx += 1

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    query = f"SELECT COUNT(*) FROM alerts {where_clause}"
    return await fetchval(query, *params)


async def get_alert_stats(station_id: UUID | None = None) -> dict:
    """Get alert statistics."""
    condition = "WHERE station_id = $1" if station_id else ""
    params = [station_id] if station_id else []

    stats = await fetchrow(
        f"""
        SELECT
            COUNT(*) as total,
            COUNT(*) FILTER (WHERE severity = 'critical') as critical,
            COUNT(*) FILTER (WHERE severity = 'high') as high,
            COUNT(*) FILTER (WHERE severity = 'medium') as medium,
            COUNT(*) FILTER (WHERE severity = 'low') as low,
            COUNT(*) FILTER (WHERE severity = 'info') as info,
            COUNT(*) FILTER (WHERE acknowledged_at IS NULL) as unacknowledged,
            COUNT(*) FILTER (WHERE resolved_at IS NULL) as unresolved
        FROM alerts
        {condition}
        """,
        *params,
    )
    return dict(stats) if stats else {}


async def get_alerts_by_station(station_id: UUID, limit: int = 10) -> list[asyncpg.Record]:
    """Get recent alerts for a station."""
    return await fetch(
        """
        SELECT id, station_id, alert_type, severity, title, message,
               acknowledged_at, resolved_at, created_at
        FROM alerts
        WHERE station_id = $1
        ORDER BY created_at DESC
        LIMIT $2
        """,
        station_id,
        limit,
    )


async def create_maintenance_record(
    station_id: UUID,
    maintenance_type: str,
    scheduled_at: datetime,
    technician_id: UUID | None = None,
    notes: str | None = None,
) -> asyncpg.Record:
    """Create a maintenance record."""
    return await fetchrow(
        """
        INSERT INTO maintenance_records (station_id, maintenance_type, scheduled_at, technician_id, notes)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING id, station_id, maintenance_type, scheduled_at, completed_at,
                  technician_id, notes, attachments, status, created_at, updated_at
        """,
        station_id,
        maintenance_type,
        scheduled_at,
        technician_id,
        notes,
    )


async def update_maintenance_record(
    maintenance_id: UUID,
    scheduled_at: datetime | None = None,
    technician_id: UUID | None = None,
    status: str | None = None,
    notes: str | None = None,
) -> asyncpg.Record | None:
    """Update a maintenance record."""
    updates = []
    params = []
    param_idx = 1

    if scheduled_at is not None:
        updates.append(f"scheduled_at = ${param_idx}")
        params.append(scheduled_at)
        param_idx += 1

    if technician_id is not None:
        updates.append(f"technician_id = ${param_idx}")
        params.append(technician_id)
        param_idx += 1

    if status is not None:
        updates.append(f"status = ${param_idx}")
        params.append(status)
        param_idx += 1

    if notes is not None:
        updates.append(f"notes = ${param_idx}")
        params.append(notes)
        param_idx += 1

    if not updates:
        return None

    params.append(maintenance_id)
    query = f"""
        UPDATE maintenance_records
        SET {", ".join(updates)}
        WHERE id = ${param_idx}
        RETURNING id, station_id, maintenance_type, scheduled_at, completed_at,
                  technician_id, notes, attachments, status, created_at, updated_at
    """
    return await fetchrow(query, *params)


async def complete_maintenance(
    maintenance_id: UUID,
    notes: str | None = None,
    attachments: list[str] | None = None,
) -> asyncpg.Record | None:
    """Complete a maintenance record."""
    return await fetchrow(
        """
        UPDATE maintenance_records
        SET completed_at = NOW(),
            status = 'completed',
            notes = COALESCE($2, notes),
            attachments = COALESCE($3, attachments)
        WHERE id = $1
        RETURNING id, station_id, maintenance_type, scheduled_at, completed_at,
                  technician_id, notes, attachments, status, created_at, updated_at
        """,
        maintenance_id,
        notes,
        attachments,
    )


async def list_maintenance_records(
    station_id: UUID | None = None,
    status: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[asyncpg.Record]:
    """List maintenance records with optional filters."""
    conditions = []
    params = []
    param_idx = 1

    if station_id is not None:
        conditions.append(f"m.station_id = ${param_idx}")
        params.append(station_id)
        param_idx += 1

    if status is not None:
        conditions.append(f"m.status = ${param_idx}")
        params.append(status)
        param_idx += 1

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    params.extend([limit, offset])
    query = f"""
        SELECT m.id, m.station_id, s.name as station_name, m.maintenance_type,
               m.scheduled_at, m.completed_at, m.status, u.full_name as technician_name
        FROM maintenance_records m
        LEFT JOIN stations s ON m.station_id = s.id
        LEFT JOIN users u ON m.technician_id = u.id
        {where_clause}
        ORDER BY m.scheduled_at DESC
        LIMIT ${param_idx} OFFSET ${param_idx + 1}
    """
    return await fetch(query, *params)
