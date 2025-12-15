"""Station API endpoints."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from src.api.deps import AdminUser, CurrentUser, OperatorUser
from src.core.exceptions import ConflictError, NotFoundError
from src.models.base import (
    ApiListResponse,
    ApiResponse,
    MessageResponse,
    PaginationMeta,
)
from src.models.station import (
    StationCreateRequest,
    StationListItemResponse,
    StationResponse,
    StationStatus,
    StationUpdateRequest,
)
from src.services.station import service as station_service

router = APIRouter(prefix="/stations", tags=["Stations"])


@router.post("", response_model=ApiResponse[StationResponse], status_code=status.HTTP_201_CREATED)
async def create_station(_: AdminUser, request: StationCreateRequest):
    """Create a new lighthouse station."""
    try:
        station = await station_service.create_station(request)
        return ApiResponse(data=station)
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.message)


@router.get("", response_model=ApiListResponse[StationListItemResponse])
async def list_stations(
    _: CurrentUser,
    page: int = 1,
    limit: int = 20,
    status: StationStatus | None = None,
    region_id: UUID | None = None,
    search: str | None = None,
):
    """List all stations with filters."""
    stations, total = await station_service.list_stations(
        page=page,
        limit=limit,
        status=status,
        region_id=region_id,
        search=search,
    )
    return ApiListResponse(
        data=stations,
        meta=PaginationMeta(
            page=page,
            limit=limit,
            total=total,
            has_more=(page * limit) < total,
        ),
    )


@router.get("/{station_id}", response_model=ApiResponse[StationResponse])
async def get_station(_: CurrentUser, station_id: UUID):
    """Get a station by ID."""
    try:
        station = await station_service.get_station(station_id)
        return ApiResponse(data=station)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.put("/{station_id}", response_model=ApiResponse[StationResponse])
async def update_station(_: OperatorUser, station_id: UUID, request: StationUpdateRequest):
    """Update a station."""
    try:
        station = await station_service.update_station(station_id, request)
        return ApiResponse(data=station)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.delete("/{station_id}", response_model=ApiResponse[MessageResponse])
async def delete_station(_: AdminUser, station_id: UUID):
    """Delete a station."""
    try:
        await station_service.delete_station(station_id)
        return ApiResponse(data=MessageResponse(message="Station deleted"))
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get("/code/{code}", response_model=ApiResponse[StationResponse])
async def get_station_by_code(_: CurrentUser, code: str):
    """Get a station by code."""
    try:
        station = await station_service.get_station_by_code(code)
        return ApiResponse(data=station)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get("/region/{region_id}", response_model=ApiResponse[list[StationListItemResponse]])
async def get_stations_by_region(_: CurrentUser, region_id: UUID):
    """Get all stations in a region."""
    stations = await station_service.get_stations_by_region(region_id)
    return ApiResponse(data=stations)
