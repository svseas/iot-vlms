"""Telemetry-related Pydantic models."""

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field

from src.models.base import BaseSchema


class MetricType(str, Enum):
    """Types of telemetry metrics."""

    BATTERY_VOLTAGE = "battery_voltage"
    BATTERY_CURRENT = "battery_current"
    BATTERY_SOC = "battery_soc"
    BATTERY_TEMPERATURE = "battery_temperature"
    SOLAR_VOLTAGE = "solar_voltage"
    SOLAR_CURRENT = "solar_current"
    SOLAR_POWER = "solar_power"
    LOAD_POWER = "load_power"
    LIGHT_STATUS = "light_status"
    LIGHT_INTENSITY = "light_intensity"
    LIGHT_POWER = "light_power"
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    WIND_SPEED = "wind_speed"
    WIND_DIRECTION = "wind_direction"
    PRESSURE = "pressure"
    SIGNAL_STRENGTH = "signal_strength"


class DeviceType(str, Enum):
    """Types of IoT devices."""

    GATEWAY = "gateway"
    SENSOR_POWER = "sensor_power"
    SENSOR_SECURITY = "sensor_security"
    CAMERA = "camera"
    SENSOR_FIRE = "sensor_fire"


class DeviceStatus(str, Enum):
    """Device operational status."""

    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"
    MAINTENANCE = "maintenance"


# Sensor Data Models (defined first for forward references)


class GatewayData(BaseModel):
    """Gateway telemetry data."""

    firmware: str | None = None
    signal_strength: int | None = None
    uptime_seconds: int | None = None


class PowerSensorData(BaseModel):
    """Power sensor readings."""

    battery_voltage: float | None = None
    battery_current: float | None = None
    solar_voltage: float | None = None
    solar_current: float | None = None
    load_power: float | None = None


class LightSensorData(BaseModel):
    """Light sensor readings."""

    status: str | None = None
    intensity: int | None = None
    rotation_rpm: float | None = None


class SecuritySensorData(BaseModel):
    """Security sensor readings."""

    pir_1: bool | None = None
    pir_2: bool | None = None
    door_sensor: str | None = None
    tamper: bool | None = None


class EnvironmentSensorData(BaseModel):
    """Environment sensor readings."""

    temperature: float | None = None
    humidity: float | None = None


class FireSensorData(BaseModel):
    """Fire sensor readings."""

    smoke_detector: bool | None = None
    heat_detector: bool | None = None


class SensorData(BaseModel):
    """Complete sensor data payload."""

    power: PowerSensorData | None = None
    light: LightSensorData | None = None
    security: SecuritySensorData | None = None
    environment: EnvironmentSensorData | None = None
    fire: FireSensorData | None = None


# Request Models


class TelemetryIngestRequest(BaseModel):
    """Request model for ingesting telemetry data."""

    station_id: str
    timestamp: datetime
    gateway: GatewayData | None = None
    sensors: SensorData


class TelemetryQueryRequest(BaseModel):
    """Request model for querying telemetry data."""

    station_id: UUID | None = None
    device_id: UUID | None = None
    metric_type: MetricType | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None


class TelemetryAggregateRequest(BaseModel):
    """Request model for aggregated telemetry query."""

    station_id: UUID
    metric_type: MetricType
    start_time: datetime
    end_time: datetime
    interval: str = Field(default="1 hour", pattern=r"^\d+\s+(minute|hour|day)s?$")


# Response Models


class TelemetryResponse(BaseSchema):
    """Response model for a single telemetry record."""

    time: datetime
    station_id: UUID
    device_id: UUID
    metric_type: MetricType
    value: float
    unit: str | None
    quality: int


class TelemetryAggregateResponse(BaseModel):
    """Response model for aggregated telemetry data."""

    bucket: datetime
    station_id: UUID
    metric_type: MetricType
    avg_value: float
    min_value: float
    max_value: float
    sample_count: int


class DeviceResponse(BaseSchema):
    """Response model for device data."""

    id: UUID
    station_id: UUID
    device_type: DeviceType
    model: str | None
    serial_number: str | None
    firmware_version: str | None
    last_seen_at: datetime | None
    status: DeviceStatus
    config: dict | None
    created_at: datetime


class TelemetryLatestResponse(BaseModel):
    """Response model for latest telemetry values per metric."""

    station_id: UUID
    metrics: dict[str, float | str]
    last_update: datetime
