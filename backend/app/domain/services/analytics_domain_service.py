from datetime import UTC, datetime

from app.domain.monitoring import (
    Anomaly,
    AnomalySeverity,
    AnomalyType,
    ChargerStatus,
    TelemetryEvent,
)


class AnalyticsDomainService:
    """Evaluates telemetry events against simple operational monitoring rules."""

    def evaluate(self, telemetry_event: TelemetryEvent) -> list[Anomaly]:
        if telemetry_event.id is None:
            raise ValueError("TelemetryEvent must be persisted before anomaly detection")

        anomalies: list[Anomaly] = []

        if telemetry_event.status == ChargerStatus.FAULTED:
            anomalies.append(
                self._create_anomaly(
                    telemetry_event=telemetry_event,
                    anomaly_type=AnomalyType.CHARGER_FAULT,
                    severity=AnomalySeverity.HIGH,
                    description="Charger reported FAULTED status.",
                )
            )

        if telemetry_event.error_code is not None:
            anomalies.append(
                self._create_anomaly(
                    telemetry_event=telemetry_event,
                    anomaly_type=AnomalyType.ERROR_CODE_DETECTED,
                    severity=AnomalySeverity.HIGH,
                    description="Telemetry event contains an operational error code.",
                )
            )

        if (
            telemetry_event.status == ChargerStatus.CHARGING
            and telemetry_event.power.power_kw == 0
        ):
            anomalies.append(
                self._create_anomaly(
                    telemetry_event=telemetry_event,
                    anomaly_type=AnomalyType.POWER_ANOMALY,
                    severity=AnomalySeverity.MEDIUM,
                    description="Charger reports CHARGING status but no power output.",
                )
            )

        if telemetry_event.status in {ChargerStatus.UNAVAILABLE, ChargerStatus.OFFLINE}:
            anomalies.append(
                self._create_anomaly(
                    telemetry_event=telemetry_event,
                    anomaly_type=AnomalyType.CHARGER_UNAVAILABLE,
                    severity=AnomalySeverity.MEDIUM,
                    description="Charger is unavailable for operation.",
                )
            )

        return anomalies

    @staticmethod
    def _create_anomaly(
        telemetry_event: TelemetryEvent,
        anomaly_type: AnomalyType,
        severity: AnomalySeverity,
        description: str,
    ) -> Anomaly:
        return Anomaly(
            telemetry_event_id=telemetry_event.id,
            charger_id=telemetry_event.charger_id,
            connector_id=telemetry_event.connector_id,
            anomaly_type=anomaly_type,
            severity=severity,
            description=description,
            detected_at=datetime.now(UTC),
        )
