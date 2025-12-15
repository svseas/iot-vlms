"""Station-related Pydantic models."""

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field

from src.models.base import BaseSchema, TimestampMixin


class StationStatus(str, Enum):
    """Station operational status."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    DECOMMISSIONED = "decommissioned"


class Location(BaseModel):
    """Geographic location."""

    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)


# Request Models


class StationCreateRequest(BaseModel):
    """Request model for creating a station."""

    code: str = Field(min_length=1, max_length=20)
    name: str = Field(min_length=1, max_length=255)
    location: Location
    region_id: UUID | None = None
    metadata: dict | None = None


class StationUpdateRequest(BaseModel):
    """Request model for updating a station."""

    name: str | None = Field(None, min_length=1, max_length=255)
    location: Location | None = None
    region_id: UUID | None = None
    status: StationStatus | None = None
    metadata: dict | None = None


class StationListRequest(BaseModel):
    """Request model for listing stations with filters."""

    status: StationStatus | None = None
    region_id: UUID | None = None
    search: str | None = None


# Response Models


class StationResponse(BaseSchema, TimestampMixin):
    """Response model for station data."""

    id: UUID
    code: str
    name: str
    location: Location
    region_id: UUID | None
    status: StationStatus
    commissioned_at: datetime | None
    metadata: dict | None


class StationListItemResponse(BaseSchema):
    """Response model for station list item."""

    id: UUID
    code: str
    name: str
    location: Location
    status: StationStatus
    region_id: UUID | None
    created_at: datetime


class StationStatusResponse(BaseModel):
    """Response model for real-time station status."""

    station_id: UUID
    light_status: str
    battery_voltage: float
    solar_power: float
    connection_status: str
    last_update: datetime


class RegionResponse(BaseSchema, TimestampMixin):
    """Response model for region data."""

    id: UUID
    name: str
    code: str
    station_count: int = 0
