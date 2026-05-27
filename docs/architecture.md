# Architecture

VoltEdge Operational Monitoring is structured around the Operational Monitoring bounded context.

The MVP follows this value chain:

Telemetry Monitoring -> Anomaly Detection -> Operational Insights

The current MVP implements Telemetry Monitoring, Anomaly Detection, read-only Operational Insights, a browser dashboard and a small RabbitMQ integration queue. Alerting, authentication, Kafka and full background processing are intentionally left out of scope.

## Components

- FastAPI backend exposes operational monitoring endpoints under `/api`.
- PostgreSQL stores TelemetryEvent and Anomaly records for Charger and Connector monitoring.
- RabbitMQ receives `telemetry.created` events after telemetry is persisted.
- SQLAlchemy provides persistence mapping between the API and PostgreSQL.
- Pydantic validates inbound telemetry data.
- AnalyticsDomainService evaluates stored TelemetryEvent data against simple monitoring rules, calculates OperationalInsight read models and assigns an explainable incident risk score for BI prioritization.
- The demo telemetry simulator can act as a controlled Charger data source for Power BI demos.
- Docker Compose runs the backend, PostgreSQL and RabbitMQ services together.

## Domain Concepts

- Charger identifies the EV charger that produced telemetry.
- Connector identifies the physical charging connector on a charger.
- TelemetryEvent is the stored operational event submitted by the platform.
- TelemetryCreatedEvent is the JSON message published to RabbitMQ after persistence.
- ChargerStatus represents the current charger state.
- ErrorCode represents a known operational error when one is present.
- PowerMeasurement is represented by `power_kw`.
- Heartbeat is represented by `heartbeat_at`.
- Anomaly represents a detected operational issue from telemetry.
- MonitoringRule is represented by simple rule logic in the AnalyticsDomainService.
- OperationalInsight is represented by API read models calculated from TelemetryEvent and Anomaly data.
- IncidentRisk is represented by `incident_risk_score` and `incident_risk_level` on BI-ready records.
- Alert is a future concept and is not implemented.

## Data Flow

1. A charger sends a TelemetryEvent to `POST /api/telemetry`.
2. The API validates the Charger, Connector, ChargerStatus, PowerMeasurement, ErrorCode and Heartbeat fields.
3. The backend stores the event in PostgreSQL.
4. The AnalyticsDomainService evaluates the stored TelemetryEvent.
5. If a rule detects an operational issue, the backend stores one or more Anomaly records.
6. The backend publishes a `telemetry.created` message to the RabbitMQ queue `telemetry.events`.
7. Operators can read stored telemetry through `GET /api/telemetry`.
8. Operators can read detected anomalies through `GET /api/anomalies`.
9. Operators can read operational insights through `GET /api/insights/summary`, `GET /api/insights/charger-health` and `GET /api/insights/anomaly-rate`.
10. The browser dashboard reads API data from `/dashboard`.
11. Power BI can read charger-level insight records with incident risk through `GET /api/bi/operational-insights`.

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

The BI endpoint also exposes a simple incident risk model:

- `incident_risk_score` ranges from 0 to 100.
- `incident_risk_level` is `LOW`, `MEDIUM` or `HIGH`.
- The score is based on latest status, anomaly rate, severity counts and average power output.

This is intentionally not a production machine learning pipeline. It is an explainable MVP analysis model that supports the Operational Monitoring domain concept of Incident Risk without adding model training, ML infrastructure or background processing.

## RabbitMQ Integration

RabbitMQ is used as a small integration queue, not as the primary data store. PostgreSQL remains the source of truth for telemetry and anomalies.

The backend publishes this message type:

```text
event_type: telemetry.created
queue: telemetry.events
```

The message contains the telemetry event fields and the number of anomalies created for that telemetry event. In a later version, a worker, alert service or integration service could consume this queue asynchronously. In the MVP, the queue demonstrates how Operational Monitoring can evolve toward event-driven processing without introducing RabbitMQ as a dependency for dashboard reads or core insight calculations.

## Sprint 3: Operational Insights

Sprint 3 completes the MVP value chain by exposing simple operational insight endpoints based on the existing TelemetryEvent and Anomaly data. The implementation stays read-only for insights and does not introduce background jobs or an `operational_insights` database table.
