"""IoT data simulator for VLMS demo.

Generates realistic telemetry data for lighthouse stations including:
- Solar panel metrics (voltage, current, power)
- Battery metrics (voltage, SOC, temperature)
- Weather data (temperature, humidity, wind, pressure)
- Light status (intensity, operational hours)
- Security sensors (motion events)
"""

import asyncio
import random
import math
import os
from datetime import datetime, timezone
from uuid import UUID

import asyncpg


class LighthouseSimulator:
    """Simulates IoT sensor data for a lighthouse station."""

    def __init__(self, station_id: UUID, devices: dict[str, UUID]):
        self.station_id = station_id
        self.devices = devices
        self.hour = datetime.now(timezone.utc).hour

        # State variables for realistic simulation
        self.battery_soc = random.uniform(70, 100)
        self.light_on = self.hour >= 18 or self.hour < 6
        self.base_temp = random.uniform(25, 32)  # Vietnam tropical climate

    def get_solar_metrics(self) -> list[dict]:
        """Generate solar panel telemetry."""
        # Use sensor_power device for power-related metrics
        device_id = self.devices.get("sensor_power")
        if not device_id:
            return []

        # Solar production based on time of day
        hour = datetime.now(timezone.utc).hour
        if 6 <= hour <= 18:
            # Daylight hours - bell curve production
            solar_factor = math.sin((hour - 6) * math.pi / 12)
            # Add cloud cover variation
            cloud_factor = random.uniform(0.6, 1.0)
            solar_factor *= cloud_factor
        else:
            solar_factor = 0

        voltage = 12 + (solar_factor * 8) + random.uniform(-0.5, 0.5)
        current = solar_factor * 15 + random.uniform(-0.2, 0.2)
        power = voltage * current

        return [
            {
                "metric_type": "solar_voltage",
                "value": round(max(0, voltage), 2),
                "unit": "V",
                "device_id": device_id,
            },
            {
                "metric_type": "solar_current",
                "value": round(max(0, current), 2),
                "unit": "A",
                "device_id": device_id,
            },
            {
                "metric_type": "solar_power",
                "value": round(max(0, power), 2),
                "unit": "W",
                "device_id": device_id,
            },
        ]

    def get_battery_metrics(self) -> list[dict]:
        """Generate battery telemetry."""
        # Use sensor_power device for battery metrics
        device_id = self.devices.get("sensor_power")
        if not device_id:
            return []

        hour = datetime.now(timezone.utc).hour

        # Update SOC based on solar production and consumption
        if 6 <= hour <= 18:
            # Charging during day
            self.battery_soc = min(100, self.battery_soc + random.uniform(0.1, 0.5))
        else:
            # Discharging at night (light consumes power)
            self.battery_soc = max(20, self.battery_soc - random.uniform(0.2, 0.8))

        # Battery voltage based on SOC (12V system: 10.5V empty, 14.4V full)
        voltage = 10.5 + (self.battery_soc / 100) * 3.9 + random.uniform(-0.1, 0.1)

        # Temperature varies with ambient and charge state
        temp = self.base_temp + random.uniform(-2, 5)

        return [
            {
                "metric_type": "battery_voltage",
                "value": round(voltage, 2),
                "unit": "V",
                "device_id": device_id,
            },
            {
                "metric_type": "battery_soc",
                "value": round(self.battery_soc, 1),
                "unit": "%",
                "device_id": device_id,
            },
            {
                "metric_type": "battery_temperature",
                "value": round(temp, 1),
                "unit": "C",
                "device_id": device_id,
            },
        ]

    def get_weather_metrics(self) -> list[dict]:
        """Generate weather station telemetry."""
        # Use gateway device for weather data
        device_id = self.devices.get("gateway")
        if not device_id:
            return []

        hour = datetime.now(timezone.utc).hour

        # Temperature varies by time of day
        temp_offset = -3 if 0 <= hour < 6 else (5 if 12 <= hour < 15 else 0)
        temperature = self.base_temp + temp_offset + random.uniform(-1, 1)

        # Humidity inversely related to temperature
        humidity = 80 - (temperature - 25) * 2 + random.uniform(-5, 5)
        humidity = max(40, min(100, humidity))

        # Wind speed - coastal areas are windy
        wind_speed = random.uniform(5, 25)

        # Wind direction
        wind_direction = random.uniform(0, 360)

        # Barometric pressure
        pressure = 1013 + random.uniform(-10, 10)

        return [
            {
                "metric_type": "temperature",
                "value": round(temperature, 1),
                "unit": "C",
                "device_id": device_id,
            },
            {
                "metric_type": "humidity",
                "value": round(humidity, 1),
                "unit": "%",
                "device_id": device_id,
            },
            {
                "metric_type": "wind_speed",
                "value": round(wind_speed, 1),
                "unit": "km/h",
                "device_id": device_id,
            },
            {
                "metric_type": "wind_direction",
                "value": round(wind_direction, 0),
                "unit": "deg",
                "device_id": device_id,
            },
            {
                "metric_type": "pressure",
                "value": round(pressure, 1),
                "unit": "hPa",
                "device_id": device_id,
            },
        ]

    def get_light_metrics(self) -> list[dict]:
        """Generate light controller telemetry."""
        # Use gateway device for light data
        device_id = self.devices.get("gateway")
        if not device_id:
            return []

        hour = datetime.now(timezone.utc).hour
        self.light_on = hour >= 18 or hour < 6

        intensity = 100 if self.light_on else 0
        power = 350 if self.light_on else 0  # LED marine light

        return [
            {
                "metric_type": "light_intensity",
                "value": intensity,
                "unit": "%",
                "device_id": device_id,
            },
            {
                "metric_type": "light_power",
                "value": power + random.uniform(-10, 10) if power > 0 else 0,
                "unit": "W",
                "device_id": device_id,
            },
            {
                "metric_type": "light_status",
                "value": 1 if self.light_on else 0,
                "unit": "bool",
                "device_id": device_id,
            },
        ]

    def get_all_metrics(self) -> list[dict]:
        """Get all simulated metrics."""
        metrics = []
        metrics.extend(self.get_solar_metrics())
        metrics.extend(self.get_battery_metrics())
        metrics.extend(self.get_weather_metrics())
        metrics.extend(self.get_light_metrics())
        return metrics


async def generate_random_alerts(pool, stations: list[dict]):
    """Occasionally generate realistic alerts."""
    alert_scenarios = [
        ("power_failure", "high", "Low battery voltage detected", "Battery voltage dropped below 11.5V threshold"),
        ("device_offline", "medium", "Weather station offline", "No data received for 15 minutes"),
        ("anomaly", "low", "Unusual power consumption", "Power draw 20% higher than expected"),
        ("intrusion", "high", "Motion detected", "Motion sensor triggered at restricted area"),
        ("maintenance_due", "info", "Scheduled maintenance due", "Monthly inspection due in 3 days"),
    ]

    if random.random() < 0.1:  # 10% chance per cycle
        station = random.choice(stations)
        alert_type, severity, title, message = random.choice(alert_scenarios)

        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO alerts (station_id, alert_type, severity, title, message, metadata)
                VALUES ($1, $2, $3, $4, $5, $6)
                """,
                station["id"],
                alert_type,
                severity,
                title,
                message,
                {"simulated": True, "timestamp": datetime.now(timezone.utc).isoformat()},
            )
            print(f"  Alert generated: [{severity.upper()}] {title} at {station['name']}")


async def run_simulation(pool, interval: int = 30):
    """Run continuous telemetry simulation."""
    async with pool.acquire() as conn:
        # Get all stations and their devices
        stations = await conn.fetch(
            """
            SELECT s.id, s.code, s.name
            FROM stations s
            WHERE s.status = 'active'
            """
        )

        if not stations:
            print("No active stations found. Run seed_data.py first.")
            return

        # Get devices for each station
        simulators = {}
        for station in stations:
            devices = await conn.fetch(
                """
                SELECT id, device_type FROM devices WHERE station_id = $1
                """,
                station["id"],
            )
            device_map = {d["device_type"]: d["id"] for d in devices}
            simulators[station["id"]] = LighthouseSimulator(station["id"], device_map)

        print(f"Simulating {len(stations)} stations...")
        print(f"Generating telemetry every {interval} seconds")
        print("Press Ctrl+C to stop\n")

        cycle = 0
        while True:
            cycle += 1
            now = datetime.now(timezone.utc)
            print(f"[{now.strftime('%H:%M:%S')}] Cycle {cycle}")

            for station in stations:
                sim = simulators[station["id"]]
                metrics = sim.get_all_metrics()

                # Insert telemetry records
                for metric in metrics:
                    await conn.execute(
                        """
                        INSERT INTO telemetry (time, station_id, device_id, metric_type, value, unit, quality)
                        VALUES ($1, $2, $3, $4, $5, $6, $7)
                        """,
                        now,
                        station["id"],
                        metric["device_id"],
                        metric["metric_type"],
                        metric["value"],
                        metric["unit"],
                        100,
                    )

                print(f"  {station['code']}: {len(metrics)} metrics recorded")

            # Occasionally generate alerts
            await generate_random_alerts(pool, list(stations))

            await asyncio.sleep(interval)


async def main():
    """Main entry point."""
    print("=" * 50)
    print("VLMS IoT Data Simulator")
    print("=" * 50)

    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL environment variable is required")
        return

    pool = await asyncpg.create_pool(dsn=database_url, min_size=2, max_size=5)

    try:
        await run_simulation(pool, interval=30)
    except KeyboardInterrupt:
        print("\n\nSimulation stopped.")
    finally:
        await pool.close()


if __name__ == "__main__":
    asyncio.run(main())
