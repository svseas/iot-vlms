"""AI service using PydanticAI with Gemini for predictive analytics."""

import logging
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from pydantic_ai import Agent

from src.core.config import get_settings
from src.db.queries import telemetry as telemetry_queries
from src.db.queries import alerts as alert_queries
from src.models.telemetry import MetricType

logger = logging.getLogger(__name__)


class AnalysisResult(BaseModel):
    """Result of AI analysis."""

    summary: str
    risk_level: str
    recommendations: list[str]
    predicted_issues: list[str]
    confidence: float


class MaintenancePrediction(BaseModel):
    """Predicted maintenance needs."""

    component: str
    urgency: str
    reason: str
    recommended_action: str
    estimated_days_until_failure: int | None


class AnomalyDetection(BaseModel):
    """Detected anomaly in telemetry data."""

    metric: str
    current_value: float
    expected_range: str
    severity: str
    possible_causes: list[str]


def _get_agent() -> Agent:
    """Get a PydanticAI agent configured with Gemini."""
    settings = get_settings()
    return Agent(
        model=f"google-gla:gemini-1.5-flash",
        system_prompt="""You are an AI assistant specialized in lighthouse monitoring systems.
You analyze telemetry data from IoT sensors to:
1. Detect anomalies in power, environment, and security sensors
2. Predict maintenance needs before failures occur
3. Provide actionable recommendations for operators

Always provide structured, actionable insights based on the data provided.
Consider patterns across multiple metrics when making assessments.""",
    )


async def analyze_station_health(station_id: UUID) -> AnalysisResult:
    """Analyze overall health of a lighthouse station."""
    latest = await telemetry_queries.get_latest_telemetry(station_id)
    recent_alerts = await alert_queries.get_alerts_by_station(station_id, limit=20)

    metrics_summary = "\n".join([f"- {k}: {v}" for k, v in [(r["metric_type"], r["value"]) for r in latest]])

    alerts_summary = "\n".join([
        f"- [{a['severity']}] {a['title']} ({a['created_at']})"
        for a in recent_alerts[:10]
    ]) if recent_alerts else "No recent alerts"

    prompt = f"""Analyze the health of this lighthouse station based on the following data:

Current Sensor Readings:
{metrics_summary}

Recent Alerts (last 10):
{alerts_summary}

Provide a structured analysis including:
1. Overall health summary (1-2 sentences)
2. Risk level (low/medium/high/critical)
3. Top 3 recommendations
4. Potential issues to watch
5. Confidence level (0-1)

Format your response as:
SUMMARY: <summary>
RISK_LEVEL: <level>
RECOMMENDATIONS:
- <rec1>
- <rec2>
- <rec3>
PREDICTED_ISSUES:
- <issue1>
- <issue2>
CONFIDENCE: <0-1>"""

    agent = _get_agent()
    result = await agent.run(prompt)

    response_text = result.data
    lines = response_text.strip().split("\n")

    summary = ""
    risk_level = "medium"
    recommendations = []
    predicted_issues = []
    confidence = 0.7

    current_section = None
    for line in lines:
        line = line.strip()
        if line.startswith("SUMMARY:"):
            summary = line.replace("SUMMARY:", "").strip()
        elif line.startswith("RISK_LEVEL:"):
            risk_level = line.replace("RISK_LEVEL:", "").strip().lower()
        elif line.startswith("RECOMMENDATIONS:"):
            current_section = "recommendations"
        elif line.startswith("PREDICTED_ISSUES:"):
            current_section = "issues"
        elif line.startswith("CONFIDENCE:"):
            try:
                confidence = float(line.replace("CONFIDENCE:", "").strip())
            except ValueError:
                confidence = 0.7
        elif line.startswith("-") and current_section:
            item = line.lstrip("- ").strip()
            if current_section == "recommendations":
                recommendations.append(item)
            elif current_section == "issues":
                predicted_issues.append(item)

    return AnalysisResult(
        summary=summary or "Analysis completed",
        risk_level=risk_level,
        recommendations=recommendations[:5],
        predicted_issues=predicted_issues[:5],
        confidence=min(max(confidence, 0), 1),
    )


async def predict_maintenance(station_id: UUID) -> list[MaintenancePrediction]:
    """Predict maintenance needs for a station."""
    latest = await telemetry_queries.get_latest_telemetry(station_id)

    metrics_data = {r["metric_type"]: r["value"] for r in latest}

    prompt = f"""Based on these lighthouse sensor readings, predict maintenance needs:

Sensor Data:
- Battery Voltage: {metrics_data.get('battery_voltage', 'N/A')} V
- Solar Power: {metrics_data.get('solar_power', 'N/A')} W
- Temperature: {metrics_data.get('temperature', 'N/A')} °C
- Signal Strength: {metrics_data.get('signal_strength', 'N/A')} dBm

For each component that may need maintenance, provide:
1. Component name
2. Urgency (routine/soon/urgent/critical)
3. Reason for maintenance
4. Recommended action
5. Estimated days until potential failure (if applicable)

Format each prediction as:
COMPONENT: <name>
URGENCY: <level>
REASON: <why>
ACTION: <what to do>
DAYS: <number or N/A>
---"""

    agent = _get_agent()
    result = await agent.run(prompt)

    predictions = []
    current = {}

    for line in result.data.strip().split("\n"):
        line = line.strip()
        if line == "---" and current:
            predictions.append(MaintenancePrediction(
                component=current.get("component", "Unknown"),
                urgency=current.get("urgency", "routine"),
                reason=current.get("reason", ""),
                recommended_action=current.get("action", ""),
                estimated_days_until_failure=current.get("days"),
            ))
            current = {}
        elif line.startswith("COMPONENT:"):
            current["component"] = line.replace("COMPONENT:", "").strip()
        elif line.startswith("URGENCY:"):
            current["urgency"] = line.replace("URGENCY:", "").strip().lower()
        elif line.startswith("REASON:"):
            current["reason"] = line.replace("REASON:", "").strip()
        elif line.startswith("ACTION:"):
            current["action"] = line.replace("ACTION:", "").strip()
        elif line.startswith("DAYS:"):
            days_str = line.replace("DAYS:", "").strip()
            try:
                current["days"] = int(days_str) if days_str.lower() != "n/a" else None
            except ValueError:
                current["days"] = None

    if current:
        predictions.append(MaintenancePrediction(
            component=current.get("component", "Unknown"),
            urgency=current.get("urgency", "routine"),
            reason=current.get("reason", ""),
            recommended_action=current.get("action", ""),
            estimated_days_until_failure=current.get("days"),
        ))

    return predictions


async def detect_anomalies(
    station_id: UUID,
    start_time: datetime,
    end_time: datetime,
) -> list[AnomalyDetection]:
    """Detect anomalies in telemetry data for a time period."""
    anomalies = []

    for metric in [MetricType.BATTERY_VOLTAGE, MetricType.TEMPERATURE, MetricType.SIGNAL_STRENGTH]:
        aggregates = await telemetry_queries.get_telemetry_aggregates(
            station_id=station_id,
            metric_type=metric.value,
            start_time=start_time,
            end_time=end_time,
        )

        if not aggregates:
            continue

        values = [a["avg_value"] for a in aggregates]
        if not values:
            continue

        avg = sum(values) / len(values)
        latest = values[0] if values else avg

        thresholds = {
            MetricType.BATTERY_VOLTAGE: (10.5, 14.5, "V"),
            MetricType.TEMPERATURE: (0, 55, "°C"),
            MetricType.SIGNAL_STRENGTH: (-100, -50, "dBm"),
        }

        if metric in thresholds:
            low, high, unit = thresholds[metric]
            if latest < low or latest > high:
                severity = "critical" if (latest < low * 0.9 or latest > high * 1.1) else "warning"
                anomalies.append(AnomalyDetection(
                    metric=metric.value,
                    current_value=latest,
                    expected_range=f"{low}-{high} {unit}",
                    severity=severity,
                    possible_causes=_get_possible_causes(metric, latest, low, high),
                ))

    return anomalies


def _get_possible_causes(metric: MetricType, value: float, low: float, high: float) -> list[str]:
    """Get possible causes for an anomaly based on metric type."""
    causes = {
        MetricType.BATTERY_VOLTAGE: {
            "low": ["Battery degradation", "Insufficient solar charging", "High power consumption"],
            "high": ["Overcharging", "Faulty charge controller", "Sensor malfunction"],
        },
        MetricType.TEMPERATURE: {
            "low": ["Equipment not generating heat", "Possible equipment failure"],
            "high": ["Poor ventilation", "Equipment overheating", "Fire hazard"],
        },
        MetricType.SIGNAL_STRENGTH: {
            "low": ["Antenna issue", "Interference", "Weather conditions"],
            "high": ["Unusual - verify sensor calibration"],
        },
    }

    if metric not in causes:
        return ["Unknown cause"]

    return causes[metric]["low" if value < low else "high"]
