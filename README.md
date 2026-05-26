# VoltEdge Mobility A/S - Operational Monitoring

VoltEdge Operational Monitoring er en backend-baseret MVP til operationel overvågning af EV-ladere. Projektet viser, hvordan en digital platform kan modtage telemetridata fra ladere, gemme data i PostgreSQL og analysere driftsdata for at opdage simple operationelle afvigelser.

Systemet følger værdikæden:

Telemetry Monitoring -> Anomaly Detection -> Operational Insights

Den nuværende løsning implementerer hele MVP-værdikæden i en simpel backend: modtagelse og lagring af TelemetryEvent-data, regelbaseret oprettelse af Anomaly-records og API-baserede Operational Insights. Power BI-dashboard, RabbitMQ, frontend, alerting, authentication og CI/CD er ikke en del af den nuværende implementation.

## Funktionalitet

- FastAPI-backend til Operational Monitoring API'et.
- PostgreSQL-database til lagring af TelemetryEvent- og Anomaly-records.
- SQLAlchemy som persistence layer.
- Pydantic schemas til validering af API-requests og responses.
- AnalyticsDomainService til regelbaseret anomaly detection og simple operational insights.
- Docker Compose-stack med backend- og PostgreSQL-services.
- Pytest-tests for telemetry flow, anomaly detection, operational insights og API-endpoints.

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

I den nuværende implementation er MonitoringRule repræsenteret som simple regler i AnalyticsDomainService. OperationalInsight er implementeret som read models/API-responses baseret på eksisterende TelemetryEvent- og Anomaly-data. Alert er et fremtidigt domænebegreb, men er ikke implementeret endnu.

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
Operational Insights
        |
        v
GET /api/insights/*
```

Når et TelemetryEvent oprettes via API'et, gemmes eventet først i PostgreSQL. Derefter evaluerer AnalyticsDomainService eventet mod de simple overvågningsregler. Hvis en regel matcher, gemmes en eller flere Anomaly-records i databasen. Operational Insights beregnes som read-only API-responses oven på de eksisterende TelemetryEvent- og Anomaly-tabeller.

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

## Kørsel på virtuel maskine

MVP'en er designet til at blive demonstreret på projektets virtuelle maskine. Docker Compose kører både FastAPI-backend og PostgreSQL på VM'en.

SSH ind på VM'en:

```bash
ssh <user>@<VM-IP>
```

Hent nyeste kode:

```bash
git pull
```

Start applikationen på VM'en:

```bash
docker compose up -d --build
```

Tjek containerne:

```bash
docker compose ps
```

Tjek API health inde fra VM'en:

```bash
curl http://localhost:8000/api/health
```

Swagger UI kan åbnes fra browseren:

```text
http://<VM-IP>:8000/docs
```

## Lokal opsætning

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
| GET | `/api/insights/summary` | Viser samlet operationel status |
| GET | `/api/insights/charger-health` | Viser health state per Charger |
| GET | `/api/insights/anomaly-rate` | Viser anomaly rate og severity distribution |

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

Hent samlet OperationalInsight summary:

```bash
curl http://localhost:8000/api/insights/summary
```

Hent charger health:

```bash
curl http://localhost:8000/api/insights/charger-health
```

Hent anomaly rate:

```bash
curl http://localhost:8000/api/insights/anomaly-rate
```

## Lokale tests

Installer dependencies og kør tests fra backend-mappen:

```bash
cd backend
pip install -r requirements.txt
pytest
```

Testene bruger SQLite in-memory, så de kan køres uden Docker eller PostgreSQL.
