"""Telemetry service for sensor data management."""

import logging
from datetime import datetime
from uuid import UUID

from src.core.exceptions import NotFoundError
from src.db.queries import stations as station_queries
from src.db.queries import telemetry as telemetry_queries
from src.models.telemetry import (
    DeviceResponse,
    DeviceStatus,
    DeviceType,
    MetricType,
    TelemetryAggregateResponse,
    TelemetryIngestRequest,
    TelemetryLatestResponse,
    TelemetryResponse,
)

logger = logging.getLogger(__name__)


async def ingest_telemetry(request: TelemetryIngestRequest) -> None:
    """Process and store incoming telemetry data."""
    station = await station_queries.get_station_by_code(request.station_id)
    if not station:
        logger.warning("Telemetry received for unknown station", extra={"station_code": request.station_id})
        raise NotFoundError("Station", request.station_id)

    station_uuid = station["id"]
    gateway = await telemetry_queries.get_or_create_gateway(station_uuid)
    device_id = gateway["id"]

    records = []
    timestamp = request.timestamp

    if request.sensors.power:
        power = request.sensors.power
        if power.battery_voltage is not None:
            records.append({
                "time": timestamp,
                "station_id": station_uuid,
                "device_id": device_id,
                "metric_type": MetricType.BATTERY_VOLTAGE.value,
                "value": power.battery_voltage,
                "unit": "V",
            })
        if power.battery_current is not None:
            records.append({
                "time": timestamp,
                "station_id": station_uuid,
                "device_id": device_id,
                "metric_type": MetricType.BATTERY_CURRENT.value,
                "value": power.battery_current,
                "unit": "A",
            })
        if power.solar_voltage is not None:
            records.append({
                "time": timestamp,
                "station_id": station_uuid,
                "device_id": device_id,
                "metric_type": MetricType.SOLAR_VOLTAGE.value,
                "value": power.solar_voltage,
                "unit": "V",
            })
        if power.solar_current is not None:
            records.append({
                "time": timestamp,
                "station_id": station_uuid,
                "device_id": device_id,
                "metric_type": MetricType.SOLAR_CURRENT.value,
                "value": power.solar_current,
                "unit": "A",
            })
        if power.load_power is not None:
            records.append({
                "time": timestamp,
                "station_id": station_uuid,
                "device_id": device_id,
                "metric_type": MetricType.LOAD_POWER.value,
                "value": power.load_power,
                "unit": "W",
            })

    if request.sensors.environment:
        env = request.sensors.environment
        if env.temperature is not None:
            records.append({
                "time": timestamp,
                "station_id": station_uuid,
                "device_id": device_id,
                "metric_type": MetricType.TEMPERATURE.value,
                "value": env.temperature,
                "unit": "°C",
            })
        if env.humidity is not None:
            records.append({
                "time": timestamp,
                "station_id": station_uuid,
                "device_id": device_id,
                "metric_type": MetricType.HUMIDITY.value,
                "value": env.humidity,
                "unit": "%",
            })

    if request.gateway and request.gateway.signal_strength is not None:
        records.append({
            "time": timestamp,
            "station_id": station_uuid,
            "device_id": device_id,
            "metric_type": MetricType.SIGNAL_STRENGTH.value,
            "value": float(request.gateway.signal_strength),
            "unit": "dBm",
        })

    if records:
        await telemetry_queries.insert_telemetry_batch(records)
        logger.info(
            "Telemetry ingested",
            extra={"station_id": str(station_uuid), "record_count": len(records)},
        )


async def get_telemetry(
    station_id: UUID | None = None,
    device_id: UUID | None = None,
    metric_type: MetricType | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    page: int = 1,
    limit: int = 100,
) -> list[TelemetryResponse]:
    """Query telemetry data with filters."""
    offset = (page - 1) * limit

    records = await telemetry_queries.get_telemetry(
        station_id=station_id,
        device_id=device_id,
        metric_type=metric_type.value if metric_type else None,
        start_time=start_time,
        end_time=end_time,
        limit=limit,
        offset=offset,
    )

    return [
        TelemetryResponse(
            time=r["time"],
            station_id=r["station_id"],
            device_id=r["device_id"],
            metric_type=MetricType(r["metric_type"]),
            value=r["value"],
            unit=r["unit"],
            quality=r["quality"],
        )
        for r in records
    ]


async def get_telemetry_aggregates(
    station_id: UUID,
    metric_type: MetricType,
    start_time: datetime,
    end_time: datetime,
    interval: str = "1 hour",
) -> list[TelemetryAggregateResponse]:
    """Get aggregated telemetry data."""
    records = await telemetry_queries.get_telemetry_aggregates(
        station_id=station_id,
        metric_type=metric_type.value,
        start_time=start_time,
        end_time=end_time,
        interval=interval,
    )

    return [
        TelemetryAggregateResponse(
            bucket=r["bucket"],
            station_id=r["station_id"],
            metric_type=MetricType(r["metric_type"]),
            avg_value=r["avg_value"],
            min_value=r["min_value"],
            max_value=r["max_value"],
            sample_count=r["sample_count"],
        )
        for r in records
    ]


async def get_latest_telemetry(station_id: UUID) -> TelemetryLatestResponse:
    """Get the latest telemetry values for a station."""
    station = await station_queries.get_station_by_id(station_id)
    if not station:
        raise NotFoundError("Station", station_id)

    records = await telemetry_queries.get_latest_telemetry(station_id)

    metrics = {}
    last_update = None
    for r in records:
        metrics[r["metric_type"]] = r["value"]
        if last_update is None or r["time"] > last_update:
            last_update = r["time"]

    return TelemetryLatestResponse(
        station_id=station_id,
        metrics=metrics,
        last_update=last_update or datetime.now(),
    )


async def get_devices_by_station(station_id: UUID) -> list[DeviceResponse]:
    """Get all devices for a station."""
    station = await station_queries.get_station_by_id(station_id)
    if not station:
        raise NotFoundError("Station", station_id)

    devices = await telemetry_queries.get_devices_by_station(station_id)

    return [
        DeviceResponse(
            id=d["id"],
            station_id=d["station_id"],
            device_type=DeviceType(d["device_type"]),
            model=d["model"],
            serial_number=d["serial_number"],
            firmware_version=d["firmware_version"],
            last_seen_at=d["last_seen_at"],
            status=DeviceStatus(d["status"]),
            config=d["config"],
            created_at=d["created_at"],
        )
        for d in devices
    ]
