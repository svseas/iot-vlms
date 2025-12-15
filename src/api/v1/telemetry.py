"""Telemetry API endpoints."""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from src.api.deps import CurrentUser
from src.core.exceptions import NotFoundError
from src.models.base import ApiResponse
from src.models.telemetry import (
    DeviceResponse,
    MetricType,
    TelemetryAggregateResponse,
    TelemetryIngestRequest,
    TelemetryLatestResponse,
    TelemetryResponse,
)
from src.services.telemetry import service as telemetry_service

router = APIRouter(prefix="/telemetry", tags=["Telemetry"])


@router.post("/ingest", status_code=status.HTTP_202_ACCEPTED)
async def ingest_telemetry(request: TelemetryIngestRequest):
    """Ingest telemetry data from IoT gateway."""
    try:
        await telemetry_service.ingest_telemetry(request)
        return {"status": "accepted"}
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get("", response_model=ApiResponse[list[TelemetryResponse]])
async def get_telemetry(
    _: CurrentUser,
    station_id: UUID | None = None,
    device_id: UUID | None = None,
    metric_type: MetricType | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    page: int = 1,
    limit: int = 100,
):
    """Query telemetry data with filters."""
    data = await telemetry_service.get_telemetry(
        station_id=station_id,
        device_id=device_id,
        metric_type=metric_type,
        start_time=start_time,
        end_time=end_time,
        page=page,
        limit=limit,
    )
    return ApiResponse(data=data)


@router.get("/aggregates", response_model=ApiResponse[list[TelemetryAggregateResponse]])
async def get_telemetry_aggregates(
    _: CurrentUser,
    station_id: UUID,
    metric_type: MetricType,
    start_time: datetime,
    end_time: datetime,
    interval: str = "1 hour",
):
    """Get aggregated telemetry data."""
    data = await telemetry_service.get_telemetry_aggregates(
        station_id=station_id,
        metric_type=metric_type,
        start_time=start_time,
        end_time=end_time,
        interval=interval,
    )
    return ApiResponse(data=data)


@router.get("/latest/{station_id}", response_model=ApiResponse[TelemetryLatestResponse])
async def get_latest_telemetry(_: CurrentUser, station_id: UUID):
    """Get latest telemetry values for a station."""
    try:
        data = await telemetry_service.get_latest_telemetry(station_id)
        return ApiResponse(data=data)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get("/devices/{station_id}", response_model=ApiResponse[list[DeviceResponse]])
async def get_devices(_: CurrentUser, station_id: UUID):
    """Get all devices for a station."""
    try:
        devices = await telemetry_service.get_devices_by_station(station_id)
        return ApiResponse(data=devices)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
