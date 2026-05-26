from datetime import UTC, datetime
from typing import Protocol

from app.domain.monitoring import (
    Anomaly,
    AnomalyRateInsight,
    AnomalySeverity,
    AnomalyType,
    ChargerHealthInsight,
    ChargerStatus,
    HealthState,
    OperationalInsightSummary,
    TelemetryEvent,
    TopProblematicCharger,
)


class TelemetryInsightSource(Protocol):
    id: int
    charger_id: str
    status: str
    power_kw: float
    received_at: datetime


class AnomalyInsightSource(Protocol):
    charger_id: str
    severity: str


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

    def calculate_summary(
        self,
        telemetry_events: list[TelemetryInsightSource],
        anomalies: list[AnomalyInsightSource],
    ) -> OperationalInsightSummary:
        total_events = len(telemetry_events)
        total_anomalies = len(anomalies)
        anomaly_counts = self._count_anomalies_by_charger(anomalies)

        return OperationalInsightSummary(
            total_telemetry_events=total_events,
            total_anomalies=total_anomalies,
            chargers_with_anomalies=len(anomaly_counts),
            faulted_chargers=self._count_faulted_chargers(telemetry_events),
            average_power_kw=self._average_power(telemetry_events),
            anomaly_rate_percent=self._anomaly_rate(total_events, total_anomalies),
            top_problematic_chargers=self._top_problematic_chargers(anomaly_counts),
        )

    def calculate_charger_health(
        self,
        telemetry_events: list[TelemetryInsightSource],
        anomalies: list[AnomalyInsightSource],
    ) -> list[ChargerHealthInsight]:
        anomalies_by_charger = self._group_anomalies_by_charger(anomalies)
        events_by_charger = self._group_events_by_charger(telemetry_events)
        health_insights: list[ChargerHealthInsight] = []

        for charger_id in sorted(events_by_charger):
            charger_events = events_by_charger[charger_id]
            charger_anomalies = anomalies_by_charger.get(charger_id, [])
            latest_event = max(
                charger_events,
                key=lambda event: (event.received_at, event.id),
            )
            latest_status = ChargerStatus(latest_event.status)
            high_count = self._count_severity(
                charger_anomalies,
                AnomalySeverity.HIGH,
            )
            medium_count = self._count_severity(
                charger_anomalies,
                AnomalySeverity.MEDIUM,
            )

            health_insights.append(
                ChargerHealthInsight(
                    charger_id=charger_id,
                    latest_status=latest_status,
                    total_events=len(charger_events),
                    total_anomalies=len(charger_anomalies),
                    high_severity_anomalies=high_count,
                    average_power_kw=self._average_power(charger_events),
                    health_state=self._health_state(
                        latest_status,
                        high_count,
                        medium_count,
                    ),
                )
            )

        return health_insights

    def calculate_anomaly_rate(
        self,
        telemetry_events: list[TelemetryInsightSource],
        anomalies: list[AnomalyInsightSource],
    ) -> AnomalyRateInsight:
        total_events = len(telemetry_events)
        total_anomalies = len(anomalies)

        severity_distribution = {
            AnomalySeverity.HIGH: 0,
            AnomalySeverity.MEDIUM: 0,
        }
        for anomaly in anomalies:
            severity_distribution[AnomalySeverity(anomaly.severity)] += 1

        return AnomalyRateInsight(
            total_telemetry_events=total_events,
            total_anomalies=total_anomalies,
            anomaly_rate_percent=self._anomaly_rate(total_events, total_anomalies),
            severity_distribution=severity_distribution,
        )

    @staticmethod
    def _average_power(telemetry_events: list[TelemetryInsightSource]) -> float:
        if not telemetry_events:
            return 0.0

        return round(
            sum(event.power_kw for event in telemetry_events) / len(telemetry_events),
            2,
        )

    @staticmethod
    def _anomaly_rate(total_events: int, total_anomalies: int) -> float:
        if total_events == 0:
            return 0.0

        return round((total_anomalies / total_events) * 100, 2)

    @staticmethod
    def _group_events_by_charger(
        telemetry_events: list[TelemetryInsightSource],
    ) -> dict[str, list[TelemetryInsightSource]]:
        grouped: dict[str, list[TelemetryInsightSource]] = {}
        for event in telemetry_events:
            grouped.setdefault(event.charger_id, []).append(event)

        return grouped

    @staticmethod
    def _group_anomalies_by_charger(
        anomalies: list[AnomalyInsightSource],
    ) -> dict[str, list[AnomalyInsightSource]]:
        grouped: dict[str, list[AnomalyInsightSource]] = {}
        for anomaly in anomalies:
            grouped.setdefault(anomaly.charger_id, []).append(anomaly)

        return grouped

    @staticmethod
    def _count_anomalies_by_charger(
        anomalies: list[AnomalyInsightSource],
    ) -> dict[str, int]:
        counts: dict[str, int] = {}
        for anomaly in anomalies:
            counts[anomaly.charger_id] = counts.get(anomaly.charger_id, 0) + 1

        return counts

    @staticmethod
    def _count_faulted_chargers(
        telemetry_events: list[TelemetryInsightSource],
    ) -> int:
        latest_by_charger: dict[str, TelemetryInsightSource] = {}

        for event in telemetry_events:
            current = latest_by_charger.get(event.charger_id)
            if current is None or (event.received_at, event.id) > (
                current.received_at,
                current.id,
            ):
                latest_by_charger[event.charger_id] = event

        return sum(
            1
            for event in latest_by_charger.values()
            if event.status == ChargerStatus.FAULTED.value
        )

    @staticmethod
    def _top_problematic_chargers(
        anomaly_counts: dict[str, int],
    ) -> list[TopProblematicCharger]:
        sorted_chargers = sorted(
            anomaly_counts.items(),
            key=lambda item: (-item[1], item[0]),
        )

        return [
            TopProblematicCharger(charger_id=charger_id, total_anomalies=count)
            for charger_id, count in sorted_chargers[:5]
        ]

    @staticmethod
    def _count_severity(
        anomalies: list[AnomalyInsightSource],
        severity: AnomalySeverity,
    ) -> int:
        return sum(1 for anomaly in anomalies if anomaly.severity == severity.value)

    @staticmethod
    def _health_state(
        latest_status: ChargerStatus,
        high_severity_anomalies: int,
        medium_severity_anomalies: int,
    ) -> HealthState:
        if (
            latest_status in {ChargerStatus.FAULTED, ChargerStatus.OFFLINE}
            or high_severity_anomalies > 0
        ):
            return HealthState.CRITICAL

        if latest_status == ChargerStatus.UNAVAILABLE or medium_severity_anomalies > 0:
            return HealthState.WARNING

        return HealthState.HEALTHY
