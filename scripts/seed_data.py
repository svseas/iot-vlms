"""Seed database with real Vietnam lighthouse data."""

import asyncio
import json
import os

import asyncpg
import bcrypt


def hash_password(password: str) -> str:
    """Hash a password."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

# Real Vietnam lighthouse data based on ibiblio.org and other sources
LIGHTHOUSES = [
    {
        "code": "VT-001",
        "name": "Vung Tau Lighthouse",
        "lat": 10.3267,
        "lng": 107.0722,
        "metadata": {
            "height_m": 18,
            "focal_plane_m": 170,
            "range_nm": 20,
            "established": 1862,
            "characteristic": "Fl W 10s",
            "province": "Ba Ria - Vung Tau",
            "description": "Historic lighthouse on Nui Nho mountain",
        },
    },
    {
        "code": "CD-001",
        "name": "Hon Bay Canh Lighthouse",
        "lat": 8.6668,
        "lng": 106.7063,
        "metadata": {
            "height_m": 16,
            "focal_plane_m": 212,
            "range_nm": 25,
            "established": 1887,
            "characteristic": "Fl(3) W 10s",
            "province": "Con Dao Islands",
            "description": "Historic French colonial lighthouse on Bay Canh island",
        },
    },
    {
        "code": "PQ-001",
        "name": "Duong Dong Lighthouse",
        "lat": 10.2172,
        "lng": 103.9564,
        "metadata": {
            "height_m": 9,
            "focal_plane_m": 15,
            "range_nm": 15,
            "established": 1993,
            "characteristic": "Fl(3) W 9s",
            "province": "Phu Quoc Island",
            "description": "Main lighthouse of Phu Quoc island",
        },
    },
    {
        "code": "CG-001",
        "name": "Can Gio Lighthouse",
        "lat": 10.4108,
        "lng": 106.9517,
        "metadata": {
            "height_m": 22.5,
            "focal_plane_m": 22.5,
            "range_nm": 15,
            "established": 1864,
            "characteristic": "Fl(3) W 8s",
            "province": "Ho Chi Minh City",
            "description": "Historic cast iron pile lighthouse at Saigon River entrance",
        },
    },
    {
        "code": "HK-001",
        "name": "Hon Khoai Lighthouse",
        "lat": 8.4378,
        "lng": 104.8333,
        "metadata": {
            "height_m": 16,
            "focal_plane_m": 300,
            "range_nm": 25,
            "established": 1904,
            "characteristic": "Fl W 5s",
            "province": "Ca Mau",
            "description": "French colonial lighthouse on Hon Khoai island",
        },
    },
    {
        "code": "AT-001",
        "name": "An Thoi Lighthouse",
        "lat": 10.0192,
        "lng": 104.0142,
        "metadata": {
            "height_m": 14,
            "focal_plane_m": 80,
            "range_nm": 18,
            "established": 2000,
            "characteristic": "Fl(2) W 6s",
            "province": "Phu Quoc Island",
            "description": "Southern tip of Phu Quoc island",
        },
    },
    {
        "code": "TC-001",
        "name": "Tho Chu Lighthouse",
        "lat": 9.2667,
        "lng": 103.4667,
        "metadata": {
            "height_m": 18,
            "focal_plane_m": 140,
            "range_nm": 20,
            "established": 2000,
            "characteristic": "Fl(4) W 15s",
            "province": "Kien Giang",
            "description": "Remote island lighthouse near Cambodia border",
        },
    },
    {
        "code": "ND-001",
        "name": "Nam Du Lighthouse",
        "lat": 9.6333,
        "lng": 104.3833,
        "metadata": {
            "height_m": 11.5,
            "focal_plane_m": 195,
            "range_nm": 20,
            "established": 2001,
            "characteristic": "Fl(3) W 10s",
            "province": "Kien Giang",
            "description": "Nam Du archipelago main lighthouse",
        },
    },
    {
        "code": "RG-001",
        "name": "Rach Gia Lighthouse",
        "lat": 10.0167,
        "lng": 105.0833,
        "metadata": {
            "height_m": 18.5,
            "focal_plane_m": 23.5,
            "range_nm": 15,
            "established": 1993,
            "characteristic": "Fl(2) W 8s",
            "province": "Kien Giang",
            "description": "Harbor entrance lighthouse",
        },
    },
    {
        "code": "NN-001",
        "name": "Nui Nai Lighthouse",
        "lat": 10.3667,
        "lng": 104.4833,
        "metadata": {
            "height_m": 16,
            "focal_plane_m": 112,
            "range_nm": 18,
            "established": 2000,
            "characteristic": "Fl(2) W 10s",
            "province": "Kien Giang",
            "description": "Near Ha Tien on the Cambodian border",
        },
    },
    {
        "code": "DT-001",
        "name": "Da Trang Lighthouse",
        "lat": 8.7167,
        "lng": 106.6833,
        "metadata": {
            "height_m": 10,
            "focal_plane_m": 17,
            "range_nm": 10,
            "established": 2001,
            "characteristic": "Fl R 5s",
            "province": "Con Dao Islands",
            "description": "White Rock lighthouse with red light",
        },
    },
    {
        "code": "HC-001",
        "name": "Hon Chuoi Lighthouse",
        "lat": 8.6833,
        "lng": 104.6500,
        "metadata": {
            "height_m": 11,
            "focal_plane_m": 131,
            "range_nm": 15,
            "established": 1990,
            "characteristic": "Fl(2) W 7s",
            "province": "Ca Mau",
            "description": "Banana Island lighthouse",
        },
    },
]

# Sample users for demo
USERS = [
    {
        "email": "admin@vlms.com",
        "password": "admin12345",
        "full_name": "System Administrator",
        "role": "super_admin",
    },
    {
        "email": "operator@vlms.com",
        "password": "operator123",
        "full_name": "Station Operator",
        "role": "operator",
    },
    {
        "email": "technician@vlms.com",
        "password": "tech12345",
        "full_name": "Field Technician",
        "role": "technician",
    },
    {
        "email": "viewer@vlms.com",
        "password": "viewer123",
        "full_name": "Guest Viewer",
        "role": "viewer",
    },
]


async def seed_users(pool):
    """Seed demo users."""
    print("Seeding users...")
    async with pool.acquire() as conn:
        for user in USERS:
            # Check if user exists
            existing = await conn.fetchrow(
                "SELECT id FROM users WHERE email = $1", user["email"]
            )
            if existing:
                print(f"  User {user['email']} already exists, skipping")
                continue

            hashed = hash_password(user["password"])
            await conn.execute(
                """
                INSERT INTO users (email, password_hash, full_name, role, is_active)
                VALUES ($1, $2, $3, $4, true)
                """,
                user["email"],
                hashed,
                user["full_name"],
                user["role"],
            )
            print(f"  Created user: {user['email']} ({user['role']})")


async def seed_stations(pool):
    """Seed lighthouse stations."""
    print("Seeding stations...")
    async with pool.acquire() as conn:
        for lh in LIGHTHOUSES:
            # Check if station exists
            existing = await conn.fetchrow(
                "SELECT id FROM stations WHERE code = $1", lh["code"]
            )
            if existing:
                print(f"  Station {lh['code']} already exists, skipping")
                continue

            await conn.execute(
                """
                INSERT INTO stations (code, name, location, metadata, status)
                VALUES ($1, $2, ST_SetSRID(ST_MakePoint($4, $3), 4326), $5, 'active')
                """,
                lh["code"],
                lh["name"],
                lh["lat"],
                lh["lng"],
                json.dumps(lh["metadata"]),
            )
            print(f"  Created station: {lh['code']} - {lh['name']}")


async def seed_devices(pool):
    """Seed IoT devices for each station."""
    print("Seeding devices...")
    # Valid device_types: gateway, sensor_power, sensor_security, camera, sensor_fire
    device_types = [
        ("gateway", "IoT Gateway", "Raspberry Pi 4"),
        ("sensor_power", "Power Sensor", "Victron MPPT 100/50"),
        ("sensor_security", "Security Sensor", "Bosch ISC-BPQ2-W12"),
        ("camera", "Security Camera", "Hikvision DS-2CD2143G2"),
        ("sensor_fire", "Fire Sensor", "Honeywell FD7140"),
    ]

    async with pool.acquire() as conn:
        stations = await conn.fetch("SELECT id, code FROM stations")
        for station in stations:
            for dtype, dname, model in device_types:
                existing = await conn.fetchrow(
                    """
                    SELECT id FROM devices
                    WHERE station_id = $1 AND device_type = $2
                    """,
                    station["id"],
                    dtype,
                )
                if existing:
                    continue

                await conn.execute(
                    """
                    INSERT INTO devices (station_id, device_type, model, status, config)
                    VALUES ($1, $2, $3, 'online', $4)
                    """,
                    station["id"],
                    dtype,
                    model,
                    json.dumps({"name": dname}),
                )
            print(f"  Created devices for station: {station['code']}")


async def main():
    """Run database seeding."""
    print("=" * 50)
    print("VLMS Database Seeder")
    print("=" * 50)

    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL environment variable is required")
        return

    pool = await asyncpg.create_pool(dsn=database_url, min_size=2, max_size=5)

    try:
        await seed_users(pool)
        await seed_stations(pool)
        await seed_devices(pool)
        print("=" * 50)
        print("Seeding completed successfully!")
        print("=" * 50)
        print("\nDemo accounts:")
        for user in USERS:
            print(f"  {user['email']} / {user['password']} ({user['role']})")
    finally:
        await pool.close()


if __name__ == "__main__":
    asyncio.run(main())
