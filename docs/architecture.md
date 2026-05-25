# Architecture

VoltEdge Operational Monitoring is structured around the Operational Monitoring bounded context.

For milestone 1, the implemented value-chain step is:

Telemetry Monitoring -> Anomaly Detection -> Operational Insights

Only Telemetry Monitoring is implemented. Anomaly Detection, OperationalInsight generation, BI dashboards, messaging, frontend and CI/CD are intentionally left for later milestones.

## Components

- FastAPI backend exposes operational monitoring endpoints under `/api`.
- PostgreSQL stores TelemetryEvent records for Charger and Connector monitoring.
- SQLAlchemy provides persistence mapping between the API and PostgreSQL.
- Pydantic validates inbound telemetry data.
- Docker Compose runs the backend and PostgreSQL services together.

## Domain Concepts

- Charger identifies the EV charger that produced telemetry.
- Connector identifies the physical charging connector on a charger.
- TelemetryEvent is the stored operational event submitted by the platform.
- ChargerStatus represents the current charger state.
- ErrorCode represents a known operational error when one is present.
- PowerMeasurement is represented by `power_kw`.
- Heartbeat is represented by `heartbeat_at`.
- MonitoringRule, Anomaly, Alert and OperationalInsight are future concepts for the next value-chain steps.

## Data Flow

1. A charger sends a TelemetryEvent to `POST /api/telemetry`.
2. The API validates the Charger, Connector, ChargerStatus, PowerMeasurement, ErrorCode and Heartbeat fields.
3. The backend stores the event in PostgreSQL.
4. Operators or BI tooling can read stored telemetry through `GET /api/telemetry`.
