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
