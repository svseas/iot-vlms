"""Alert-related Pydantic models."""

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field

from src.models.base import BaseSchema, TimestampMixin


class AlertType(str, Enum):
    """Types of alerts."""

    FIRE = "fire"
    INTRUSION = "intrusion"
    POWER_FAILURE = "power_failure"
    DEVICE_OFFLINE = "device_offline"
    ANOMALY = "anomaly"
    MAINTENANCE_DUE = "maintenance_due"


class SeverityLevel(str, Enum):
    """Alert severity levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class MaintenanceType(str, Enum):
    """Types of maintenance."""

    SCHEDULED = "scheduled"
    CORRECTIVE = "corrective"
    EMERGENCY = "emergency"
    INSPECTION = "inspection"


class MaintenanceStatus(str, Enum):
    """Maintenance record status."""

    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


# Request Models


class AlertCreateRequest(BaseModel):
    """Request model for creating an alert."""

    station_id: UUID
    alert_type: AlertType
    severity: SeverityLevel
    title: str = Field(min_length=1, max_length=255)
    message: str | None = None
    metadata: dict | None = None


class AlertAcknowledgeRequest(BaseModel):
    """Request model for acknowledging an alert."""

    notes: str | None = None


class AlertResolveRequest(BaseModel):
    """Request model for resolving an alert."""

    resolution_notes: str | None = None


class AlertListRequest(BaseModel):
    """Request model for listing alerts with filters."""

    station_id: UUID | None = None
    alert_type: AlertType | None = None
    severity: SeverityLevel | None = None
    acknowledged: bool | None = None
    resolved: bool | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None


class MaintenanceCreateRequest(BaseModel):
    """Request model for creating a maintenance record."""

    station_id: UUID
    maintenance_type: MaintenanceType
    scheduled_at: datetime
    technician_id: UUID | None = None
    notes: str | None = None


class MaintenanceUpdateRequest(BaseModel):
    """Request model for updating a maintenance record."""

    scheduled_at: datetime | None = None
    technician_id: UUID | None = None
    status: MaintenanceStatus | None = None
    notes: str | None = None


class MaintenanceCompleteRequest(BaseModel):
    """Request model for completing a maintenance record."""

    notes: str | None = None
    attachments: list[str] | None = None


# Response Models


class AlertResponse(BaseSchema, TimestampMixin):
    """Response model for alert data."""

    id: UUID
    station_id: UUID
    alert_type: AlertType
    severity: SeverityLevel
    title: str
    message: str | None
    acknowledged_at: datetime | None
    acknowledged_by: UUID | None
    resolved_at: datetime | None
    metadata: dict | None


class AlertListItemResponse(BaseSchema):
    """Response model for alert list item."""

    id: UUID
    station_id: UUID
    station_name: str | None = None
    alert_type: AlertType
    severity: SeverityLevel
    title: str
    acknowledged_at: datetime | None
    resolved_at: datetime | None
    created_at: datetime


class AlertStatsResponse(BaseModel):
    """Response model for alert statistics."""

    total: int
    critical: int
    high: int
    medium: int
    low: int
    info: int
    unacknowledged: int
    unresolved: int


class MaintenanceResponse(BaseSchema, TimestampMixin):
    """Response model for maintenance record."""

    id: UUID
    station_id: UUID
    maintenance_type: MaintenanceType
    scheduled_at: datetime
    completed_at: datetime | None
    technician_id: UUID | None
    notes: str | None
    attachments: list[str] | None
    status: MaintenanceStatus


class MaintenanceListItemResponse(BaseSchema):
    """Response model for maintenance list item."""

    id: UUID
    station_id: UUID
    station_name: str | None = None
    maintenance_type: MaintenanceType
    scheduled_at: datetime
    completed_at: datetime | None
    status: MaintenanceStatus
    technician_name: str | None = None
