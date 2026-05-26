from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ChargerStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    CHARGING = "CHARGING"
    FAULTED = "FAULTED"
    UNAVAILABLE = "UNAVAILABLE"
    OFFLINE = "OFFLINE"


class ErrorCode(str, Enum):
    COMMUNICATION_LOSS = "COMMUNICATION_LOSS"
    CONNECTOR_LOCK_FAILURE = "CONNECTOR_LOCK_FAILURE"
    GROUND_FAULT = "GROUND_FAULT"
    OVER_TEMPERATURE = "OVER_TEMPERATURE"
    POWER_METER_FAILURE = "POWER_METER_FAILURE"


class AnomalyType(str, Enum):
    CHARGER_FAULT = "CHARGER_FAULT"
    ERROR_CODE_DETECTED = "ERROR_CODE_DETECTED"
    POWER_ANOMALY = "POWER_ANOMALY"
    CHARGER_UNAVAILABLE = "CHARGER_UNAVAILABLE"


class AnomalySeverity(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"


class HealthState(str, Enum):
    HEALTHY = "HEALTHY"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class PowerMeasurement:
    power_kw: float

    def __post_init__(self) -> None:
        if self.power_kw < 0:
            raise ValueError("PowerMeasurement cannot be negative")


@dataclass(frozen=True)
class Heartbeat:
    heartbeat_at: datetime


@dataclass(frozen=True)
class TelemetryEvent:
    id: int | None
    charger_id: str
    connector_id: str
    status: ChargerStatus
    power: PowerMeasurement
    error_code: ErrorCode | None
    heartbeat: Heartbeat


@dataclass(frozen=True)
class Anomaly:
    telemetry_event_id: int
    charger_id: str
    connector_id: str
    anomaly_type: AnomalyType
    severity: AnomalySeverity
    description: str
    detected_at: datetime


@dataclass(frozen=True)
class TopProblematicCharger:
    charger_id: str
    total_anomalies: int


@dataclass(frozen=True)
class OperationalInsightSummary:
    total_telemetry_events: int
    total_anomalies: int
    chargers_with_anomalies: int
    faulted_chargers: int
    average_power_kw: float
    anomaly_rate_percent: float
    top_problematic_chargers: list[TopProblematicCharger]


@dataclass(frozen=True)
class ChargerHealthInsight:
    charger_id: str
    latest_status: ChargerStatus
    total_events: int
    total_anomalies: int
    high_severity_anomalies: int
    average_power_kw: float
    health_state: HealthState


@dataclass(frozen=True)
class BiOperationalInsight:
    charger_id: str
    latest_status: ChargerStatus
    total_events: int
    total_anomalies: int
    high_severity_anomalies: int
    average_power_kw: float
    anomaly_rate_percent: float
    health_state: HealthState


@dataclass(frozen=True)
class AnomalyRateInsight:
    total_telemetry_events: int
    total_anomalies: int
    anomaly_rate_percent: float
    severity_distribution: dict[AnomalySeverity, int]
