# Architecture

VoltEdge Operational Monitoring is structured around the Operational Monitoring bounded context.

The MVP follows this value chain:

Telemetry Monitoring -> Anomaly Detection -> Operational Insights

Sprint 1 implemented Telemetry Monitoring. Sprint 2 implements Anomaly Detection through a domain service. OperationalInsight generation, BI dashboards, messaging, frontend, alerting, authentication and CI/CD are intentionally left for later milestones.

## Components

- FastAPI backend exposes operational monitoring endpoints under `/api`.
- PostgreSQL stores TelemetryEvent and Anomaly records for Charger and Connector monitoring.
- SQLAlchemy provides persistence mapping between the API and PostgreSQL.
- Pydantic validates inbound telemetry data.
- AnalyticsDomainService evaluates stored TelemetryEvent data against simple monitoring rules.
- Docker Compose runs the backend and PostgreSQL services together.

## Domain Concepts

- Charger identifies the EV charger that produced telemetry.
- Connector identifies the physical charging connector on a charger.
- TelemetryEvent is the stored operational event submitted by the platform.
- ChargerStatus represents the current charger state.
- ErrorCode represents a known operational error when one is present.
- PowerMeasurement is represented by `power_kw`.
- Heartbeat is represented by `heartbeat_at`.
- Anomaly represents a detected operational issue from telemetry.
- MonitoringRule is represented by simple rule logic in the AnalyticsDomainService.
- Alert and OperationalInsight are future concepts for the next value-chain steps.

## Data Flow

1. A charger sends a TelemetryEvent to `POST /api/telemetry`.
2. The API validates the Charger, Connector, ChargerStatus, PowerMeasurement, ErrorCode and Heartbeat fields.
3. The backend stores the event in PostgreSQL.
4. The AnalyticsDomainService evaluates the stored TelemetryEvent.
5. If a rule detects an operational issue, the backend stores one or more Anomaly records.
6. Operators can read stored telemetry through `GET /api/telemetry`.
7. Operators can read detected anomalies through `GET /api/anomalies`.

## Anomaly Detection Rules

| Rule | Condition | Anomaly type | Severity |
| --- | --- | --- | --- |
| Charger fault | `status` is `FAULTED` | `CHARGER_FAULT` | `HIGH` |
| Error code detected | `error_code` is not null | `ERROR_CODE_DETECTED` | `HIGH` |
| Power anomaly | `status` is `CHARGING` and `power_kw` is `0` | `POWER_ANOMALY` | `MEDIUM` |
| Charger unavailable | `status` is `UNAVAILABLE` or `OFFLINE` | `CHARGER_UNAVAILABLE` | `MEDIUM` |
