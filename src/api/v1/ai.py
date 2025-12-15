"""AI API endpoints for predictive analytics."""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from src.api.deps import CurrentUser
from src.core.exceptions import NotFoundError
from src.models.base import ApiResponse
from src.services.ai import service as ai_service
from src.services.ai.service import AnalysisResult, AnomalyDetection, MaintenancePrediction

router = APIRouter(prefix="/ai", tags=["AI"])


@router.get("/analyze/{station_id}", response_model=ApiResponse[AnalysisResult])
async def analyze_station_health(_: CurrentUser, station_id: UUID):
    """Analyze the health of a lighthouse station using AI."""
    try:
        result = await ai_service.analyze_station_health(station_id)
        return ApiResponse(data=result)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI analysis failed: {str(e)}",
        )


@router.get("/predict-maintenance/{station_id}", response_model=ApiResponse[list[MaintenancePrediction]])
async def predict_maintenance(_: CurrentUser, station_id: UUID):
    """Predict maintenance needs for a station using AI."""
    try:
        predictions = await ai_service.predict_maintenance(station_id)
        return ApiResponse(data=predictions)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}",
        )


@router.get("/anomalies/{station_id}", response_model=ApiResponse[list[AnomalyDetection]])
async def detect_anomalies(
    _: CurrentUser,
    station_id: UUID,
    start_time: datetime,
    end_time: datetime,
):
    """Detect anomalies in telemetry data for a station."""
    try:
        anomalies = await ai_service.detect_anomalies(station_id, start_time, end_time)
        return ApiResponse(data=anomalies)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Anomaly detection failed: {str(e)}",
        )
