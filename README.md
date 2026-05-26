# VoltEdge Mobility A/S - Operational Monitoring

VoltEdge Operational Monitoring er en MVP til operationel overvågning af EV-ladere. Sprint 1 implementerede Telemetry Monitoring, og Sprint 2 tilføjer Anomaly Detection:

Telemetry Monitoring -> Anomaly Detection -> Operational Insights

Operational Insights, Power BI-dashboard, RabbitMQ, frontend, alerting, authentication og CI/CD er planlagt til senere milestones og er ikke implementeret endnu.

## Arkitekturoverblik

MVP'en indeholder:

- FastAPI-backend til Operational Monitoring API'et.
- PostgreSQL-database til lagring af TelemetryEvent- og Anomaly-records.
- SQLAlchemy som persistence layer.
- Pydantic schemas til request-validering.
- AnalyticsDomainService med simple regler til anomaly detection.
- Docker Compose-stack med backend- og PostgreSQL-services.
- Pytest-tests for API'et.

Domænebegreberne i denne milestone er Charger, Connector, TelemetryEvent, ChargerStatus, ErrorCode, PowerMeasurement, Heartbeat og Anomaly. MonitoringRule er repræsenteret som simple regler i AnalyticsDomainService. Alert og OperationalInsight er fremtidige domænebegreber.

## Projektstruktur

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

## Opsætning

Kopier eksempelmiljøfilen, hvis porte eller credentials skal tilpasses:

```bash
cp .env.example .env
```

Start stacken:

```bash
docker compose up --build
```

Stop stacken:

```bash
docker compose down
```

Fjern databasevolumen:

```bash
docker compose down -v
```

## API Endpoints

| Method | Endpoint | Beskrivelse |
| --- | --- | --- |
| GET | `/api/health` | Tjekker om API'et kører |
| POST | `/api/telemetry` | Gemmer et TelemetryEvent |
| GET | `/api/telemetry` | Lister gemte TelemetryEvents |
| GET | `/api/anomalies` | Lister detekterede Anomalies |
| GET | `/api/anomalies/{id}` | Henter én detekteret Anomaly |

## Curl-eksempler

Health check:

```bash
curl http://localhost:8000/api/health
```

Opret et TelemetryEvent:

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

List gemte TelemetryEvents:

```bash
curl http://localhost:8000/api/telemetry
```

Opret et fejlramt TelemetryEvent og list detekterede Anomalies:

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

## Lokale tests

Installer dependencies og kør tests fra backend-mappen:

```bash
cd backend
pip install -r requirements.txt
pytest
```

Testene bruger SQLite in-memory, så de kan køres uden Docker eller PostgreSQL.
