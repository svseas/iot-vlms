"""Alert API endpoints."""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from src.api.deps import CurrentUser, OperatorUser
from src.core.exceptions import NotFoundError, ValidationError
from src.models.alert import (
    AlertCreateRequest,
    AlertListItemResponse,
    AlertResponse,
    AlertStatsResponse,
    AlertType,
    MaintenanceCompleteRequest,
    MaintenanceCreateRequest,
    MaintenanceListItemResponse,
    MaintenanceResponse,
    MaintenanceStatus,
    SeverityLevel,
)
from src.models.base import (
    ApiListResponse,
    ApiResponse,
    PaginationMeta,
)
from src.services.alert import service as alert_service

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.post("", response_model=ApiResponse[AlertResponse], status_code=status.HTTP_201_CREATED)
async def create_alert(_: OperatorUser, request: AlertCreateRequest):
    """Create a new alert."""
    try:
        alert = await alert_service.create_alert(request)
        return ApiResponse(data=alert)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get("", response_model=ApiListResponse[AlertListItemResponse])
async def list_alerts(
    _: CurrentUser,
    page: int = 1,
    limit: int = 20,
    station_id: UUID | None = None,
    alert_type: AlertType | None = None,
    severity: SeverityLevel | None = None,
    acknowledged: bool | None = None,
    resolved: bool | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
):
    """List alerts with filters."""
    alerts, total = await alert_service.list_alerts(
        page=page,
        limit=limit,
        station_id=station_id,
        alert_type=alert_type,
        severity=severity,
        acknowledged=acknowledged,
        resolved=resolved,
        start_date=start_date,
        end_date=end_date,
    )
    return ApiListResponse(
        data=alerts,
        meta=PaginationMeta(
            page=page,
            limit=limit,
            total=total,
            has_more=(page * limit) < total,
        ),
    )


@router.get("/stats", response_model=ApiResponse[AlertStatsResponse])
async def get_alert_stats(_: CurrentUser, station_id: UUID | None = None):
    """Get alert statistics."""
    stats = await alert_service.get_alert_stats(station_id)
    return ApiResponse(data=stats)


@router.get("/{alert_id}", response_model=ApiResponse[AlertResponse])
async def get_alert(_: CurrentUser, alert_id: UUID):
    """Get an alert by ID."""
    try:
        alert = await alert_service.get_alert(alert_id)
        return ApiResponse(data=alert)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.post("/{alert_id}/acknowledge", response_model=ApiResponse[AlertResponse])
async def acknowledge_alert(current_user: OperatorUser, alert_id: UUID):
    """Acknowledge an alert."""
    try:
        alert = await alert_service.acknowledge_alert(
            alert_id, UUID(str(current_user["id"]))
        )
        return ApiResponse(data=alert)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.post("/{alert_id}/resolve", response_model=ApiResponse[AlertResponse])
async def resolve_alert(_: OperatorUser, alert_id: UUID):
    """Resolve an alert."""
    try:
        alert = await alert_service.resolve_alert(alert_id)
        return ApiResponse(data=alert)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.get("/station/{station_id}", response_model=ApiResponse[list[AlertListItemResponse]])
async def get_station_alerts(_: CurrentUser, station_id: UUID, limit: int = 10):
    """Get recent alerts for a station."""
    try:
        alerts = await alert_service.get_alerts_by_station(station_id, limit)
        return ApiResponse(data=alerts)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


# Maintenance endpoints


@router.post("/maintenance", response_model=ApiResponse[MaintenanceResponse], status_code=status.HTTP_201_CREATED)
async def create_maintenance(_: OperatorUser, request: MaintenanceCreateRequest):
    """Create a maintenance record."""
    try:
        record = await alert_service.create_maintenance_record(request)
        return ApiResponse(data=record)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get("/maintenance", response_model=ApiResponse[list[MaintenanceListItemResponse]])
async def list_maintenance(
    _: CurrentUser,
    page: int = 1,
    limit: int = 20,
    station_id: UUID | None = None,
    status: MaintenanceStatus | None = None,
):
    """List maintenance records."""
    records = await alert_service.list_maintenance_records(
        page=page,
        limit=limit,
        station_id=station_id,
        status=status,
    )
    return ApiResponse(data=records)


@router.post("/maintenance/{maintenance_id}/complete", response_model=ApiResponse[MaintenanceResponse])
async def complete_maintenance(
    _: OperatorUser,
    maintenance_id: UUID,
    request: MaintenanceCompleteRequest,
):
    """Complete a maintenance record."""
    try:
        record = await alert_service.complete_maintenance(
            maintenance_id,
            notes=request.notes,
            attachments=request.attachments,
        )
        return ApiResponse(data=record)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
