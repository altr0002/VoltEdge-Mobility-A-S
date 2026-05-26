# VoltEdge Mobility A/S - Operational Monitoring

VoltEdge Operational Monitoring is an MVP for monitoring EV charger operations. Sprint 1 implemented Telemetry Monitoring, and Sprint 2 adds Anomaly Detection:

Telemetry Monitoring -> Anomaly Detection -> Operational Insights

Operational Insights, Power BI dashboards, RabbitMQ, frontend, alerting, authentication and CI/CD are planned for later milestones and are not implemented yet.

## Architecture Overview

The MVP contains:

- FastAPI backend for the Operational Monitoring API.
- PostgreSQL database for storing TelemetryEvent and Anomaly records.
- SQLAlchemy persistence layer.
- Pydantic schemas for request validation.
- AnalyticsDomainService for simple anomaly detection rules.
- Docker Compose stack with backend and PostgreSQL services.
- Pytest tests for the API.

Domain concepts used in this milestone include Charger, Connector, TelemetryEvent, ChargerStatus, ErrorCode, PowerMeasurement, Heartbeat and Anomaly. MonitoringRule is represented by simple rules in the AnalyticsDomainService. Alert and OperationalInsight remain future concepts.

## Project Structure

```text
backend/
  app/
    main.py
    api/
    domain/
    infrastructure/
    schemas/
  tests/
  Dockerfile
  requirements.txt

database/
  init.sql

docs/
  architecture.md
  api-examples.md
  demo-script.md

.github/
  workflows/

docker-compose.yml
README.md
.env.example
```

## Setup

Copy the example environment file if you want to customize ports or credentials:

```bash
cp .env.example .env
```

Start the stack:

```bash
docker compose up --build
```

Stop the stack:

```bash
docker compose down
```

Remove the database volume:

```bash
docker compose down -v
```

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/api/health` | Check API health |
| POST | `/api/telemetry` | Store a TelemetryEvent |
| GET | `/api/telemetry` | List stored TelemetryEvents |
| GET | `/api/anomalies` | List detected Anomalies |
| GET | `/api/anomalies/{id}` | Get one detected Anomaly |

## Curl Examples

Health:

```bash
curl http://localhost:8000/api/health
```

Create a TelemetryEvent:

```bash
curl -X POST http://localhost:8000/api/telemetry \
  -H "Content-Type: application/json" \
  -d '{
    "charger_id": "CHG-001",
    "connector_id": "CONN-1",
    "status": "CHARGING",
    "power_kw": 42.5,
    "error_code": null,
    "heartbeat_at": "2026-05-25T10:15:00Z"
  }'
```

List stored TelemetryEvents:

```bash
curl http://localhost:8000/api/telemetry
```

Create a faulty TelemetryEvent and list detected Anomalies:

```bash
curl -X POST http://localhost:8000/api/telemetry \
  -H "Content-Type: application/json" \
  -d '{
    "charger_id": "CHG-002",
    "connector_id": "CONN-2",
    "status": "FAULTED",
    "power_kw": 0,
    "error_code": "OVER_TEMPERATURE",
    "heartbeat_at": "2026-05-25T10:20:00Z"
  }'
```

```bash
curl http://localhost:8000/api/anomalies
```

## Local Tests

Install dependencies and run tests from the backend directory:

```bash
cd backend
pip install -r requirements.txt
pytest
```

The tests use SQLite in memory so they can run without Docker or PostgreSQL.
