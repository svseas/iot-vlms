"""Alert service for managing alerts and maintenance records."""

import logging
from datetime import datetime
from uuid import UUID

from src.core.exceptions import NotFoundError, ValidationError
from src.db.queries import alerts as alert_queries
from src.db.queries import stations as station_queries
from src.models.alert import (
    AlertCreateRequest,
    AlertListItemResponse,
    AlertResponse,
    AlertStatsResponse,
    AlertType,
    MaintenanceCreateRequest,
    MaintenanceListItemResponse,
    MaintenanceResponse,
    MaintenanceStatus,
    MaintenanceType,
    SeverityLevel,
)

logger = logging.getLogger(__name__)


async def create_alert(request: AlertCreateRequest) -> AlertResponse:
    """Create a new alert."""
    station = await station_queries.get_station_by_id(request.station_id)
    if not station:
        raise NotFoundError("Station", request.station_id)

    alert = await alert_queries.create_alert(
        station_id=request.station_id,
        alert_type=request.alert_type.value,
        severity=request.severity.value,
        title=request.title,
        message=request.message,
        metadata=request.metadata,
    )

    logger.info(
        "Alert created",
        extra={
            "alert_id": str(alert["id"]),
            "station_id": str(request.station_id),
            "type": request.alert_type.value,
            "severity": request.severity.value,
        },
    )

    return AlertResponse(
        id=alert["id"],
        station_id=alert["station_id"],
        alert_type=AlertType(alert["alert_type"]),
        severity=SeverityLevel(alert["severity"]),
        title=alert["title"],
        message=alert["message"],
        acknowledged_at=alert["acknowledged_at"],
        acknowledged_by=alert["acknowledged_by"],
        resolved_at=alert["resolved_at"],
        metadata=alert["metadata"],
        created_at=alert["created_at"],
        updated_at=None,
    )


async def get_alert(alert_id: UUID) -> AlertResponse:
    """Get an alert by ID."""
    alert = await alert_queries.get_alert_by_id(alert_id)
    if not alert:
        raise NotFoundError("Alert", alert_id)

    return AlertResponse(
        id=alert["id"],
        station_id=alert["station_id"],
        alert_type=AlertType(alert["alert_type"]),
        severity=SeverityLevel(alert["severity"]),
        title=alert["title"],
        message=alert["message"],
        acknowledged_at=alert["acknowledged_at"],
        acknowledged_by=alert["acknowledged_by"],
        resolved_at=alert["resolved_at"],
        metadata=alert["metadata"],
        created_at=alert["created_at"],
        updated_at=None,
    )


async def acknowledge_alert(alert_id: UUID, user_id: UUID) -> AlertResponse:
    """Acknowledge an alert."""
    alert = await alert_queries.acknowledge_alert(alert_id, user_id)
    if not alert:
        existing = await alert_queries.get_alert_by_id(alert_id)
        if not existing:
            raise NotFoundError("Alert", alert_id)
        raise ValidationError("Alert has already been acknowledged")

    logger.info(
        "Alert acknowledged",
        extra={"alert_id": str(alert_id), "user_id": str(user_id)},
    )

    return AlertResponse(
        id=alert["id"],
        station_id=alert["station_id"],
        alert_type=AlertType(alert["alert_type"]),
        severity=SeverityLevel(alert["severity"]),
        title=alert["title"],
        message=alert["message"],
        acknowledged_at=alert["acknowledged_at"],
        acknowledged_by=alert["acknowledged_by"],
        resolved_at=alert["resolved_at"],
        metadata=alert["metadata"],
        created_at=alert["created_at"],
        updated_at=None,
    )


async def resolve_alert(alert_id: UUID) -> AlertResponse:
    """Resolve an alert."""
    alert = await alert_queries.resolve_alert(alert_id)
    if not alert:
        existing = await alert_queries.get_alert_by_id(alert_id)
        if not existing:
            raise NotFoundError("Alert", alert_id)
        raise ValidationError("Alert has already been resolved")

    logger.info("Alert resolved", extra={"alert_id": str(alert_id)})

    return AlertResponse(
        id=alert["id"],
        station_id=alert["station_id"],
        alert_type=AlertType(alert["alert_type"]),
        severity=SeverityLevel(alert["severity"]),
        title=alert["title"],
        message=alert["message"],
        acknowledged_at=alert["acknowledged_at"],
        acknowledged_by=alert["acknowledged_by"],
        resolved_at=alert["resolved_at"],
        metadata=alert["metadata"],
        created_at=alert["created_at"],
        updated_at=None,
    )


async def list_alerts(
    page: int = 1,
    limit: int = 20,
    station_id: UUID | None = None,
    alert_type: AlertType | None = None,
    severity: SeverityLevel | None = None,
    acknowledged: bool | None = None,
    resolved: bool | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> tuple[list[AlertListItemResponse], int]:
    """List alerts with pagination and filters."""
    offset = (page - 1) * limit

    alerts = await alert_queries.list_alerts(
        station_id=station_id,
        alert_type=alert_type.value if alert_type else None,
        severity=severity.value if severity else None,
        acknowledged=acknowledged,
        resolved=resolved,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
    )

    total = await alert_queries.count_alerts(
        station_id=station_id,
        alert_type=alert_type.value if alert_type else None,
        severity=severity.value if severity else None,
        acknowledged=acknowledged,
        resolved=resolved,
        start_date=start_date,
        end_date=end_date,
    )

    return [
        AlertListItemResponse(
            id=a["id"],
            station_id=a["station_id"],
            station_name=a["station_name"],
            alert_type=AlertType(a["alert_type"]),
            severity=SeverityLevel(a["severity"]),
            title=a["title"],
            acknowledged_at=a["acknowledged_at"],
            resolved_at=a["resolved_at"],
            created_at=a["created_at"],
        )
        for a in alerts
    ], total


async def get_alert_stats(station_id: UUID | None = None) -> AlertStatsResponse:
    """Get alert statistics."""
    stats = await alert_queries.get_alert_stats(station_id)

    return AlertStatsResponse(
        total=stats.get("total", 0),
        critical=stats.get("critical", 0),
        high=stats.get("high", 0),
        medium=stats.get("medium", 0),
        low=stats.get("low", 0),
        info=stats.get("info", 0),
        unacknowledged=stats.get("unacknowledged", 0),
        unresolved=stats.get("unresolved", 0),
    )


async def get_alerts_by_station(station_id: UUID, limit: int = 10) -> list[AlertListItemResponse]:
    """Get recent alerts for a station."""
    station = await station_queries.get_station_by_id(station_id)
    if not station:
        raise NotFoundError("Station", station_id)

    alerts = await alert_queries.get_alerts_by_station(station_id, limit)

    return [
        AlertListItemResponse(
            id=a["id"],
            station_id=a["station_id"],
            station_name=None,
            alert_type=AlertType(a["alert_type"]),
            severity=SeverityLevel(a["severity"]),
            title=a["title"],
            acknowledged_at=a["acknowledged_at"],
            resolved_at=a["resolved_at"],
            created_at=a["created_at"],
        )
        for a in alerts
    ]


async def create_maintenance_record(request: MaintenanceCreateRequest) -> MaintenanceResponse:
    """Create a maintenance record."""
    station = await station_queries.get_station_by_id(request.station_id)
    if not station:
        raise NotFoundError("Station", request.station_id)

    record = await alert_queries.create_maintenance_record(
        station_id=request.station_id,
        maintenance_type=request.maintenance_type.value,
        scheduled_at=request.scheduled_at,
        technician_id=request.technician_id,
        notes=request.notes,
    )

    logger.info(
        "Maintenance record created",
        extra={"maintenance_id": str(record["id"]), "station_id": str(request.station_id)},
    )

    return MaintenanceResponse(
        id=record["id"],
        station_id=record["station_id"],
        maintenance_type=MaintenanceType(record["maintenance_type"]),
        scheduled_at=record["scheduled_at"],
        completed_at=record["completed_at"],
        technician_id=record["technician_id"],
        notes=record["notes"],
        attachments=record["attachments"],
        status=MaintenanceStatus(record["status"]),
        created_at=record["created_at"],
        updated_at=record["updated_at"],
    )


async def complete_maintenance(
    maintenance_id: UUID,
    notes: str | None = None,
    attachments: list[str] | None = None,
) -> MaintenanceResponse:
    """Complete a maintenance record."""
    record = await alert_queries.complete_maintenance(maintenance_id, notes, attachments)
    if not record:
        raise NotFoundError("Maintenance record", maintenance_id)

    logger.info("Maintenance completed", extra={"maintenance_id": str(maintenance_id)})

    return MaintenanceResponse(
        id=record["id"],
        station_id=record["station_id"],
        maintenance_type=MaintenanceType(record["maintenance_type"]),
        scheduled_at=record["scheduled_at"],
        completed_at=record["completed_at"],
        technician_id=record["technician_id"],
        notes=record["notes"],
        attachments=record["attachments"],
        status=MaintenanceStatus(record["status"]),
        created_at=record["created_at"],
        updated_at=record["updated_at"],
    )


async def list_maintenance_records(
    page: int = 1,
    limit: int = 20,
    station_id: UUID | None = None,
    status: MaintenanceStatus | None = None,
) -> list[MaintenanceListItemResponse]:
    """List maintenance records with filters."""
    offset = (page - 1) * limit

    records = await alert_queries.list_maintenance_records(
        station_id=station_id,
        status=status.value if status else None,
        limit=limit,
        offset=offset,
    )

    return [
        MaintenanceListItemResponse(
            id=r["id"],
            station_id=r["station_id"],
            station_name=r["station_name"],
            maintenance_type=MaintenanceType(r["maintenance_type"]),
            scheduled_at=r["scheduled_at"],
            completed_at=r["completed_at"],
            status=MaintenanceStatus(r["status"]),
            technician_name=r["technician_name"],
        )
        for r in records
    ]
