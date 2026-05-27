from pydantic import BaseModel, ConfigDict

from app.domain.monitoring import (
    AnomalySeverity,
    ChargerStatus,
    HealthState,
    IncidentRiskLevel,
)


class TopProblematicChargerRead(BaseModel):
    charger_id: str
    total_anomalies: int

    model_config = ConfigDict(from_attributes=True)


class OperationalInsightSummaryRead(BaseModel):
    total_telemetry_events: int
    total_anomalies: int
    chargers_with_anomalies: int
    faulted_chargers: int
    average_power_kw: float
    anomaly_rate_percent: float
    top_problematic_chargers: list[TopProblematicChargerRead]

    model_config = ConfigDict(from_attributes=True)


class ChargerHealthInsightRead(BaseModel):
    charger_id: str
    latest_status: ChargerStatus
    total_events: int
    total_anomalies: int
    high_severity_anomalies: int
    average_power_kw: float
    health_state: HealthState

    model_config = ConfigDict(from_attributes=True)


class BiOperationalInsightRead(BaseModel):
    charger_id: str
    latest_status: ChargerStatus
    total_events: int
    total_anomalies: int
    high_severity_anomalies: int
    average_power_kw: float
    anomaly_rate_percent: float
    incident_risk_score: int
    incident_risk_level: IncidentRiskLevel
    health_state: HealthState

    model_config = ConfigDict(from_attributes=True)


class AnomalyRateInsightRead(BaseModel):
    total_telemetry_events: int
    total_anomalies: int
    anomaly_rate_percent: float
    severity_distribution: dict[AnomalySeverity, int]

    model_config = ConfigDict(from_attributes=True)
