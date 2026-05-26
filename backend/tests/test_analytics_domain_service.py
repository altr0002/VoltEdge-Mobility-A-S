from datetime import UTC, datetime

from app.domain.monitoring import (
    AnomalySeverity,
    AnomalyType,
    ChargerStatus,
    ErrorCode,
    Heartbeat,
    PowerMeasurement,
    TelemetryEvent,
)
from app.domain.services.analytics_domain_service import AnalyticsDomainService


def _telemetry_event(
    status: ChargerStatus,
    power_kw: float = 42.5,
    error_code: ErrorCode | None = None,
) -> TelemetryEvent:
    return TelemetryEvent(
        id=1,
        charger_id="CHG-001",
        connector_id="CONN-1",
        status=status,
        power=PowerMeasurement(power_kw),
        error_code=error_code,
        heartbeat=Heartbeat(datetime(2026, 5, 25, 10, 15, tzinfo=UTC)),
    )


def test_normal_telemetry_event_does_not_create_anomaly():
    service = AnalyticsDomainService()

    anomalies = service.evaluate(_telemetry_event(ChargerStatus.CHARGING, 42.5))

    assert anomalies == []


def test_faulted_telemetry_event_creates_charger_fault_anomaly():
    service = AnalyticsDomainService()

    anomalies = service.evaluate(_telemetry_event(ChargerStatus.FAULTED, 0))

    assert len(anomalies) == 1
    assert anomalies[0].anomaly_type == AnomalyType.CHARGER_FAULT
    assert anomalies[0].severity == AnomalySeverity.HIGH


def test_error_code_creates_error_code_detected_anomaly():
    service = AnalyticsDomainService()

    anomalies = service.evaluate(
        _telemetry_event(
            ChargerStatus.CHARGING,
            20,
            ErrorCode.OVER_TEMPERATURE,
        )
    )

    assert len(anomalies) == 1
    assert anomalies[0].anomaly_type == AnomalyType.ERROR_CODE_DETECTED
    assert anomalies[0].severity == AnomalySeverity.HIGH


def test_charging_with_zero_power_creates_power_anomaly():
    service = AnalyticsDomainService()

    anomalies = service.evaluate(_telemetry_event(ChargerStatus.CHARGING, 0))

    assert len(anomalies) == 1
    assert anomalies[0].anomaly_type == AnomalyType.POWER_ANOMALY
    assert anomalies[0].severity == AnomalySeverity.MEDIUM


def test_unavailable_telemetry_event_creates_unavailable_anomaly():
    service = AnalyticsDomainService()

    anomalies = service.evaluate(_telemetry_event(ChargerStatus.OFFLINE, 0))

    assert len(anomalies) == 1
    assert anomalies[0].anomaly_type == AnomalyType.CHARGER_UNAVAILABLE
    assert anomalies[0].severity == AnomalySeverity.MEDIUM
