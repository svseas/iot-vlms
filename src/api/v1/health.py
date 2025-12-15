"""Health check endpoints."""

import logging

from fastapi import APIRouter, HTTPException, status

from src.core.database import fetchval

router = APIRouter(tags=["Health"])
logger = logging.getLogger(__name__)


@router.get("/ping")
async def ping():
    """Simple liveness check - no dependencies."""
    return {"status": "ok"}


@router.get("/health")
async def health_check():
    """Check application health."""
    try:
        await fetchval("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error("Health check failed", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unhealthy",
        )


@router.get("/ready")
async def readiness_check():
    """Check if application is ready to serve requests."""
    try:
        await fetchval("SELECT 1")
        return {"status": "ready"}
    except Exception as e:
        logger.error("Readiness check failed", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service not ready",
        )
