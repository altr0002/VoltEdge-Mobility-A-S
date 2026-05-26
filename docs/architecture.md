# Architecture

VoltEdge Operational Monitoring is structured around the Operational Monitoring bounded context.

The MVP follows this value chain:

Telemetry Monitoring -> Anomaly Detection -> Operational Insights

The current MVP implements Telemetry Monitoring, Anomaly Detection and read-only Operational Insights. BI dashboards, messaging, frontend, alerting, authentication and CI/CD are intentionally left out of scope.

## Components

- FastAPI backend exposes operational monitoring endpoints under `/api`.
- PostgreSQL stores TelemetryEvent and Anomaly records for Charger and Connector monitoring.
- SQLAlchemy provides persistence mapping between the API and PostgreSQL.
- Pydantic validates inbound telemetry data.
- AnalyticsDomainService evaluates stored TelemetryEvent data against simple monitoring rules and calculates OperationalInsight read models.
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
- OperationalInsight is represented by API read models calculated from TelemetryEvent and Anomaly data.
- Alert is a future concept and is not implemented.

## Data Flow

1. A charger sends a TelemetryEvent to `POST /api/telemetry`.
2. The API validates the Charger, Connector, ChargerStatus, PowerMeasurement, ErrorCode and Heartbeat fields.
3. The backend stores the event in PostgreSQL.
4. The AnalyticsDomainService evaluates the stored TelemetryEvent.
5. If a rule detects an operational issue, the backend stores one or more Anomaly records.
6. Operators can read stored telemetry through `GET /api/telemetry`.
7. Operators can read detected anomalies through `GET /api/anomalies`.
8. Operators can read operational insights through `GET /api/insights/summary`, `GET /api/insights/charger-health` and `GET /api/insights/anomaly-rate`.

## Anomaly Detection Rules

| Rule | Condition | Anomaly type | Severity |
| --- | --- | --- | --- |
| Charger fault | `status` is `FAULTED` | `CHARGER_FAULT` | `HIGH` |
| Error code detected | `error_code` is not null | `ERROR_CODE_DETECTED` | `HIGH` |
| Power anomaly | `status` is `CHARGING` and `power_kw` is `0` | `POWER_ANOMALY` | `MEDIUM` |
| Charger unavailable | `status` is `UNAVAILABLE` or `OFFLINE` | `CHARGER_UNAVAILABLE` | `MEDIUM` |

## Operational Insights

Operational Insights are calculated on demand from existing PostgreSQL data. The MVP does not create an `operational_insights` table.

- `GET /api/insights/summary` returns total event counts, anomaly counts, average power, anomaly rate and top problematic chargers.
- `GET /api/insights/charger-health` returns one health row per Charger.
- `GET /api/insights/anomaly-rate` returns anomaly rate and severity distribution.
- `GET /api/bi/operational-insights` returns flat BI-ready records for Power BI or similar reporting tools.

Charger health is calculated with simple deterministic rules:

- `CRITICAL` if latest status is `FAULTED` or `OFFLINE`, or the charger has at least one `HIGH` severity anomaly.
- `WARNING` if latest status is `UNAVAILABLE`, or the charger has `MEDIUM` severity anomalies.
- `HEALTHY` otherwise.

## Sprint 3: Operational Insights

Sprint 3 completes the MVP value chain by exposing simple operational insight endpoints based on the existing TelemetryEvent and Anomaly data. The implementation stays read-only for insights and does not introduce Power BI, frontend, messaging, background jobs or an `operational_insights` database table.
