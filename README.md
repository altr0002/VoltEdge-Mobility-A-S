# VoltEdge Operational Monitoring MVP

VoltEdge Operational Monitoring MVP er en backend-baseret eksamens-MVP til operationel overvågning af EV-ladere for VoltEdge Mobility A/S.

Projektet demonstrerer, hvordan en fremtidig digital platform kan modtage telemetridata fra ladere, gemme data i PostgreSQL, udføre regelbaseret anomaly detection og eksponere operational insights via API'er.

## Bounded Context

Den primære bounded context er:

```text
Operational Monitoring
```

## MVP Value Chain

```text
Telemetry Monitoring -> Anomaly Detection -> Operational Insights
```

## Implementeret Funktionalitet

- Telemetry ingestion via FastAPI.
- Persistence af TelemetryEvent-data i PostgreSQL.
- Pydantic-validering af API-requests og responses.
- SQLAlchemy som persistence layer.
- Regelbaseret anomaly detection i AnalyticsDomainService.
- Persistence af Anomaly-records i PostgreSQL.
- Operational Insights API baseret på eksisterende telemetry/anomaly-data.
- BI / Power BI-ready API endpoint.
- Docker Compose runtime med backend og PostgreSQL.
- Pytest-tests for telemetry, anomalies, insights og BI endpoint.
- GitHub Actions CI til testkørsel.
- VM-baseret demo flow.

## Ikke En Del Af MVP'en

Dette er ikke en fuld produktionsplatform. Følgende er bevidst uden for scope:

- Real OCPP integration.
- Frontend dashboard.
- Authentication og authorization.
- RabbitMQ eller Kafka.
- Billing, payment og partner contracts.
- Real alert notifications via email/SMS.
- Production machine learning eller predictive maintenance pipeline.
- Kubernetes.
- Terraform.
- Production cloud deployment.

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
Operational Insights / BI-ready API
```

FastAPI-backenden er det operationelle system. Power BI kan efterfølgende forbinde til backendens BI-endpoint som en uafhængig analytics- og visualiseringsplatform.

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
  power-bi-guide.md

scripts/
  seed_demo_data.py

.github/
  workflows/
    ci.yml

docker-compose.yml
README.md
.env.example
```

## Kørsel På Virtuel Maskine

MVP'en er beregnet til at blive kørt på projektets virtuelle maskine med Docker Compose.

SSH ind på VM'en:

```bash
ssh <user>@<VM-IP>
```

Gå til repoet og hent nyeste kode:

```bash
cd VoltEdge-Mobility-A-S
git pull
```

Start backend og PostgreSQL:

```bash
docker compose up -d --build
```

Tjek containerne:

```bash
docker compose ps
```

Tjek API health fra VM'en:

```bash
curl http://localhost:8000/api/health
```

Åbn Swagger UI fra browser:

```text
http://<VM-IP>:8000/docs
```

## Demo Data

Når Docker Compose kører på VM'en, kan demo data oprettes med:

```bash
python3 scripts/seed_demo_data.py
```

Scriptet opretter eksempeldata for:

- en HEALTHY charger
- en WARNING charger
- en CRITICAL charger
- FAULTED status
- error_code anomaly
- CHARGING med `power_kw = 0`
- UNAVAILABLE/OFFLINE charger

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
| GET | `/api/bi/operational-insights` | Returnerer flade BI-ready records |

## Curl Eksempler Til Demo

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

Vis telemetry:

```bash
curl http://localhost:8000/api/telemetry
```

Vis anomalies:

```bash
curl http://localhost:8000/api/anomalies
```

Vis operational insights:

```bash
curl http://localhost:8000/api/insights/summary
curl http://localhost:8000/api/insights/charger-health
curl http://localhost:8000/api/insights/anomaly-rate
```

Vis BI-ready data:

```bash
curl http://localhost:8000/api/bi/operational-insights
```

## Demo Flow

1. Start Docker Compose på VM'en.
2. Seed demo data eller POST telemetry events manuelt.
3. Vis `GET /api/telemetry`.
4. Vis `GET /api/anomalies`.
5. Vis Operational Insights endpoints.
6. Vis BI-ready endpointet.
7. Vis at tests passer.
8. Vis GitHub Actions workflowet i repository.

## Tests

Kør tests fra backend-mappen:

```bash
cd backend
pytest
```

Hvis dependencies ikke er installeret:

```bash
cd backend
pip install -r requirements.txt
pytest
```

Testene bruger SQLite in-memory, så de kan køres uden Docker eller PostgreSQL.

## GitHub Actions CI

Repositoryet indeholder et simpelt CI-workflow:

```text
.github/workflows/ci.yml
```

Workflowet kører på `push` og `pull_request`, installerer backend dependencies og kører `pytest`.

## Power BI

Power BI kan forbinde til:

```text
http://<VM-IP>:8000/api/bi/operational-insights
```

Se [docs/power-bi-guide.md](docs/power-bi-guide.md) for forslag til Power BI-forbindelse og dashboard-visuals.
