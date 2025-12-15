"""Station service for lighthouse station management."""

import logging
from uuid import UUID

from src.core.exceptions import ConflictError, NotFoundError
from src.db.queries import stations as station_queries
from src.models.station import (
    Location,
    StationCreateRequest,
    StationListItemResponse,
    StationResponse,
    StationStatus,
    StationUpdateRequest,
)

logger = logging.getLogger(__name__)


async def create_station(request: StationCreateRequest) -> StationResponse:
    """Create a new lighthouse station."""
    if await station_queries.check_code_exists(request.code):
        raise ConflictError(f"Station code '{request.code}' already exists")

    station = await station_queries.create_station(
        code=request.code,
        name=request.name,
        lat=request.location.lat,
        lng=request.location.lng,
        region_id=request.region_id,
        metadata=request.metadata,
    )

    logger.info("Station created", extra={"station_id": str(station["id"]), "code": request.code})

    return StationResponse(
        id=station["id"],
        code=station["code"],
        name=station["name"],
        location=Location(lat=station["lat"], lng=station["lng"]),
        region_id=station["region_id"],
        status=StationStatus(station["status"]),
        commissioned_at=station["commissioned_at"],
        metadata=station["metadata"],
        created_at=station["created_at"],
        updated_at=station["updated_at"],
    )


async def get_station(station_id: UUID) -> StationResponse:
    """Get a station by ID."""
    station = await station_queries.get_station_by_id(station_id)
    if not station:
        raise NotFoundError("Station", station_id)

    return StationResponse(
        id=station["id"],
        code=station["code"],
        name=station["name"],
        location=Location(lat=station["lat"], lng=station["lng"]),
        region_id=station["region_id"],
        status=StationStatus(station["status"]),
        commissioned_at=station["commissioned_at"],
        metadata=station["metadata"],
        created_at=station["created_at"],
        updated_at=station["updated_at"],
    )


async def get_station_by_code(code: str) -> StationResponse:
    """Get a station by code."""
    station = await station_queries.get_station_by_code(code)
    if not station:
        raise NotFoundError("Station", code)

    return StationResponse(
        id=station["id"],
        code=station["code"],
        name=station["name"],
        location=Location(lat=station["lat"], lng=station["lng"]),
        region_id=station["region_id"],
        status=StationStatus(station["status"]),
        commissioned_at=station["commissioned_at"],
        metadata=station["metadata"],
        created_at=station["created_at"],
        updated_at=station["updated_at"],
    )


async def update_station(station_id: UUID, request: StationUpdateRequest) -> StationResponse:
    """Update a station."""
    existing = await station_queries.get_station_by_id(station_id)
    if not existing:
        raise NotFoundError("Station", station_id)

    station = await station_queries.update_station(
        station_id=station_id,
        name=request.name,
        lat=request.location.lat if request.location else None,
        lng=request.location.lng if request.location else None,
        region_id=request.region_id,
        status=request.status.value if request.status else None,
        metadata=request.metadata,
    )

    logger.info("Station updated", extra={"station_id": str(station_id)})

    return StationResponse(
        id=station["id"],
        code=station["code"],
        name=station["name"],
        location=Location(lat=station["lat"], lng=station["lng"]),
        region_id=station["region_id"],
        status=StationStatus(station["status"]),
        commissioned_at=station["commissioned_at"],
        metadata=station["metadata"],
        created_at=station["created_at"],
        updated_at=station["updated_at"],
    )


async def delete_station(station_id: UUID) -> None:
    """Delete a station."""
    success = await station_queries.delete_station(station_id)
    if not success:
        raise NotFoundError("Station", station_id)

    logger.info("Station deleted", extra={"station_id": str(station_id)})


async def list_stations(
    page: int = 1,
    limit: int = 20,
    status: StationStatus | None = None,
    region_id: UUID | None = None,
    search: str | None = None,
) -> tuple[list[StationListItemResponse], int]:
    """List stations with pagination and filters."""
    offset = (page - 1) * limit

    stations = await station_queries.list_stations(
        limit=limit,
        offset=offset,
        status=status.value if status else None,
        region_id=region_id,
        search=search,
    )

    total = await station_queries.count_stations(
        status=status.value if status else None,
        region_id=region_id,
        search=search,
    )

    return [
        StationListItemResponse(
            id=s["id"],
            code=s["code"],
            name=s["name"],
            location=Location(lat=s["lat"], lng=s["lng"]),
            status=StationStatus(s["status"]),
            region_id=s["region_id"],
            created_at=s["created_at"],
        )
        for s in stations
    ], total


async def get_stations_by_region(region_id: UUID) -> list[StationListItemResponse]:
    """Get all stations in a region."""
    stations = await station_queries.get_stations_by_region(region_id)

    return [
        StationListItemResponse(
            id=s["id"],
            code=s["code"],
            name=s["name"],
            location=Location(lat=s["lat"], lng=s["lng"]),
            status=StationStatus(s["status"]),
            region_id=region_id,
            created_at=s["created_at"],
        )
        for s in stations
    ]
