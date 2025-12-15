"""Main API v1 router that aggregates all endpoint routers."""

from fastapi import APIRouter

from src.api.v1 import ai, alerts, health, stations, telemetry, users

router = APIRouter(prefix="/api/v1")

router.include_router(health.router)
router.include_router(users.router)
router.include_router(stations.router)
router.include_router(telemetry.router)
router.include_router(alerts.router)
router.include_router(ai.router)
