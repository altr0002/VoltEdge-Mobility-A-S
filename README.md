# VoltEdge Mobility A/S - Operational Monitoring

VoltEdge Operational Monitoring er en backend-baseret MVP til operationel overvågning af EV-ladere. Projektet viser, hvordan en digital platform kan modtage telemetridata fra ladere, gemme data i PostgreSQL og analysere driftsdata for at opdage simple operationelle afvigelser.

Systemet følger værdikæden:

Telemetry Monitoring -> Anomaly Detection -> Operational Insights

Den nuværende løsning fokuserer på de to første dele: modtagelse og lagring af TelemetryEvent-data samt regelbaseret oprettelse af Anomaly-records. Operational Insights, Power BI-dashboard, RabbitMQ, frontend, alerting, authentication og CI/CD er ikke en del af den nuværende implementation.

## Funktionalitet

- FastAPI-backend til Operational Monitoring API'et.
- PostgreSQL-database til lagring af TelemetryEvent- og Anomaly-records.
- SQLAlchemy som persistence layer.
- Pydantic schemas til validering af API-requests og responses.
- AnalyticsDomainService til regelbaseret anomaly detection.
- Docker Compose-stack med backend- og PostgreSQL-services.
- Pytest-tests for telemetry flow, anomaly detection og API-endpoints.

## Domænemodel

Projektet er bygget omkring bounded contexten Operational Monitoring.

Centrale domænebegreber:

- Charger
- Connector
- TelemetryEvent
- ChargerStatus
- ErrorCode
- PowerMeasurement
- Heartbeat
- Anomaly
- MonitoringRule
- OperationalInsight
- Alert

I den nuværende implementation er MonitoringRule repræsenteret som simple regler i AnalyticsDomainService. OperationalInsight og Alert er medtaget som fremtidige domænebegreber, men er ikke implementeret endnu.

## Arkitekturoverblik

```text
Client / Charger Simulator
        |
        v
FastAPI API
        |
        v
TelemetryEvent persistence
        |
        v
AnalyticsDomainService
        |
        v
Anomaly persistence
        |
        v
GET /api/anomalies
```

Når et TelemetryEvent oprettes via API'et, gemmes eventet først i PostgreSQL. Derefter evaluerer AnalyticsDomainService eventet mod de simple overvågningsregler. Hvis en regel matcher, gemmes en eller flere Anomaly-records i databasen.

## Anomaly Detection-regler

| Regel | Betingelse | Anomaly type | Severity |
| --- | --- | --- | --- |
| Charger fault | `status` er `FAULTED` | `CHARGER_FAULT` | `HIGH` |
| Error code detected | `error_code` er ikke `null` | `ERROR_CODE_DETECTED` | `HIGH` |
| Power anomaly | `status` er `CHARGING` og `power_kw` er `0` | `POWER_ANOMALY` | `MEDIUM` |
| Charger unavailable | `status` er `UNAVAILABLE` eller `OFFLINE` | `CHARGER_UNAVAILABLE` | `MEDIUM` |

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

## Teknologier

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Pydantic
- Docker og Docker Compose
- Pytest

## Opsætning

Kopier eksempelmiljøfilen, hvis porte eller credentials skal tilpasses:

```bash
cp .env.example .env
```

Start stacken:

```bash
docker compose up --build
```

API'et er herefter tilgængeligt på:

```text
http://localhost:8000
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
| POST | `/api/telemetry` | Gemmer et TelemetryEvent og evaluerer anomaly-regler |
| GET | `/api/telemetry` | Lister gemte TelemetryEvents |
| GET | `/api/anomalies` | Lister detekterede Anomalies |
| GET | `/api/anomalies/{id}` | Henter én detekteret Anomaly |

API-dokumentation kan åbnes i browseren:

```text
http://localhost:8000/docs
```

## Curl-eksempler

Health check:

```bash
curl http://localhost:8000/api/health
```

Opret et normalt TelemetryEvent:

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

Opret et fejlramt TelemetryEvent:

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

List detekterede Anomalies:

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
