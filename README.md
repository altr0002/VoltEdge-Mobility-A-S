# VoltEdge Operational Monitoring

VoltEdge Operational Monitoring is an MVP for monitoring EV charger operations. The first milestone implements Telemetry Monitoring, the first step in the value chain:

Telemetry Monitoring -> Anomaly Detection -> Operational Insights

Anomaly detection, analytics services, Power BI dashboards, RabbitMQ, frontend and CI/CD are planned for later milestones and are not implemented yet.

## Architecture Overview

The MVP contains:

- FastAPI backend for the Operational Monitoring API.
- PostgreSQL database for storing TelemetryEvent records.
- SQLAlchemy persistence layer.
- Pydantic schemas for request validation.
- Docker Compose stack with backend and PostgreSQL services.
- Pytest tests for the API.

Domain concepts used in this milestone include Charger, Connector, TelemetryEvent, ChargerStatus, ErrorCode, PowerMeasurement and Heartbeat. MonitoringRule, Anomaly, Alert and OperationalInsight remain future concepts.

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

## Local Tests

Install dependencies and run tests from the backend directory:

```bash
cd backend
pip install -r requirements.txt
pytest
```

The tests use SQLite in memory so they can run without Docker or PostgreSQL.
