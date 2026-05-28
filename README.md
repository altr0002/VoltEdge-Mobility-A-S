# VoltEdge Operational Monitoring MVP

VoltEdge Operational Monitoring MVP er en backend-baseret eksamens-MVP til operationel overvågning af EV-ladere for VoltEdge Mobility A/S.

Projektet demonstrerer, hvordan en fremtidig digital platform kan modtage telemetridata fra ladere, gemme data i PostgreSQL, udføre regelbaseret anomaly detection og eksponere operational insights via API'er.

## Bounded Contexts

MVP'en er opdelt i to microservices med hver sit bounded context:

```text
Telemetry Collection
Operational Insights
```

## MVP Value Chain

```text
Telemetry Monitoring -> Anomaly Detection -> Operational Insights
```

## Implementeret Funktionalitet

- Telemetry ingestion via FastAPI.
- Separat Telemetry Service til indsamling og persistence af livedata.
- Separat Insights Service til KPI'er, anomalies, risk score og dashboard.
- Persistence af TelemetryEvent-data i PostgreSQL.
- Pydantic-validering af API-requests og responses.
- SQLAlchemy som persistence layer.
- Regelbaseret anomaly detection i AnalyticsDomainService.
- Persistence af Anomaly-records i PostgreSQL.
- Operational Insights API baseret på eksisterende telemetry/anomaly-data.
- BI-ready API endpoint til dashboard og eventuel ekstern analytics.
- Simpel incident risk score til prioritering af chargers i dashboardet.
- Telemetry simulator til realistiske demo-data via VM-API'et.
- RabbitMQ-kø til `telemetry.created` events efter database-persistence.
- Browserbaseret dashboard til livedata, anomalies, KPI'er og trends.
- Jupyter Notebook til Random Forest-baseret predictive maintenance prototype.
- Docker Compose runtime med to FastAPI-services, PostgreSQL, RabbitMQ og Jupyter.
- Pytest-tests for telemetry, anomalies, insights og BI endpoint.
- GitHub Actions CI/CD til testkørsel og simpel deployment til VM.
- VM-baseret demo flow.

## Ikke En Del Af MVP'en

Dette er ikke en fuld produktionsplatform. Følgende er bevidst uden for scope:

- Real OCPP integration.
- Stort SPA-frontend med separat frontend-framework.
- Authentication og authorization.
- Kafka eller event streaming-platform.
- Billing, payment og partner contracts.
- Real alert notifications via email/SMS.
- Production machine learning eller predictive maintenance pipeline.
- Deployment eller drift af en egentlig production ML-model.
- Kubernetes.
- Terraform.
- Production cloud deployment.

## Arkitekturoverblik

```text
Client / Charger Simulator
        |
        v
Public Gateway :8000
        |\
        | \-> Insights Service :8001
        v
Telemetry Service :8002
        |
        v
TelemetryEvent persistence
        |\
        | \-> RabbitMQ telemetry.created queue
        v
AnalyticsDomainService
        |
        v
Anomaly persistence
        |
        v
Insights Service :8001
        |
        v
Operational Insights / Dashboard / BI-ready API

Jupyter Notebook :8888
        |
        v
PostgreSQL telemetry/anomaly data
        |
        v
Random Forest predictive maintenance prototype
```

Telemetry Service er write-side for livedata. Insights Service er read-side for KPI'er, anomalies, risk score og dashboard. Gatewayen er kun en simpel HTTP-indgang på VM'ens åbne port `8000`, så browser og simulator kan bruge samme offentlige adresse. PostgreSQL fungerer som fælles persistence/read model i MVP'en, mens RabbitMQ bruges som integrationskø for `telemetry.created` events efter persistence. Jupyter bruges som separat analytics-miljø til at træne og evaluere Random Forest-notebooken på de samme telemetry- og anomaly-data.

## Projektstruktur

```text
backend/
  app/
    main.py
    insights_main.py
    api/
    domain/
    infrastructure/
    schemas/
  tests/
  Dockerfile
  requirements.txt

database/
  init.sql

scripts/
  seed_demo_data.py
  simulate_demo_data.py

gateway/
  nginx.conf

jupyter/
  Dockerfile

notebooks/
  predictive_maintenance.ipynb

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

Start gateway, Telemetry Service, Insights Service, PostgreSQL, RabbitMQ og Jupyter:

```bash
docker compose up -d --build
```

Tjek containerne:

```bash
docker compose ps
```

Tjek service health fra VM'en:

```bash
curl http://localhost:8000/api/health
curl http://localhost:8002/api/health
curl http://localhost:8001/api/health
```

Åbn Swagger UI fra browser:

```text
Dashboard / Insights via gateway: http://<VM-IP>:8000/docs
Telemetry Service internt på VM: http://localhost:8002/docs
Insights Service internt på VM:  http://localhost:8001/docs
```

Åbn operational dashboard fra browser:

```text
http://<VM-IP>:8000/dashboard
```

Dette dashboard fungerer som MVP'ens simple browserbaserede BI/analytics dashboard. Det visualiserer driftsdata fra ladestandere som KPI'er, anomaly-status, charger health, risk score og seneste telemetry events.

Dashboardet understøtter eksamenskravet om Business Intelligence / analytics visualisering, fordi rå telemetry-data bliver omsat til beslutningsstøtte: driftsteamet kan se hvilke ladestandere der har problemer, hvor ofte anomalies opstår, og hvilke enheder der bør prioriteres.

MVP'en bruger ikke Power BI som selve visualiseringsværktøj. I denne MVP demonstreres BI-princippet gennem API'et `/api/bi/operational-insights` og dashboardet på `/dashboard`.

Åbn Jupyter Notebook fra browser via gatewayen:

```text
http://<VM-IP>:8000/jupyter/?token=voltedge
```

Notebooken ligger her:

```text
notebooks/predictive_maintenance.ipynb
```

Jupyter-containeren bruger samme PostgreSQL-database som backend-services via `DATABASE_URL`. Notebooken træner en Random Forest-prototype på `telemetry_events` og `anomalies`, hvor målet er at estimere, om en charger får en anomaly inden for de næste fem telemetry events. Modellen er en analytics-prototype og ikke en produktionsklar ML-service.

Åbn RabbitMQ Management UI via SSH tunnel fra din Mac:

```bash
ssh -L 15672:localhost:15672 VMVoltEdge
```

Hold SSH-vinduet åbent, og åbn derefter:

```text
http://localhost:15672
```

Login:

```text
user: voltedge
password: voltedge
```

RabbitMQ-køen hedder:

```text
telemetry.events
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

Til dashboard- og Jupyter-demo kan der oprettes en større, realistisk telemetry-historik med:

```bash
python3 scripts/simulate_demo_data.py --base-url http://<VM-IP>:8000
```

Simulatoren poster events gennem det offentlige API. Derfor bliver data valideret,
gemt og evalueret af de samme anomaly-regler som almindelig telemetry.

Kør simulatoren før Jupyter-notebooken, hvis modellen skal trænes på et større datagrundlag. Notebooken læser direkte fra PostgreSQL og forventer, at tabellerne `telemetry_events` og `anomalies` indeholder demo-data.

## Incident Risk Score

BI-endpointet returnerer en simpel, forklarbar incident risk score:

```text
incident_risk_score: 0-100
incident_risk_level: LOW / MEDIUM / HIGH
```

Scoren er ikke en production machine learning-model. Den er en ML-inspireret
analysemodel til MVP'en, hvor kendte driftsfeatures som status, anomaly rate,
high severity anomalies og power-output omsættes til et prioriteringstal for
driftsteamet.

## Predictive Maintenance Notebook

`notebooks/predictive_maintenance.ipynb` er en separat Random Forest-analyse. Den bruger repoets faktiske datamodel:

```text
telemetry_events: id, charger_id, connector_id, status, power_kw, error_code, heartbeat_at, received_at
anomalies: id, telemetry_event_id, charger_id, anomaly_type, severity, detected_at
```

Notebooken laver features som status, error-code indikator, power output og rolling anomaly metrics pr. charger. Derefter trænes en Random Forest-model med tidsbaseret train/test split. Resultatet demonstrerer predictive maintenance-potentialet, mens backendens `/api/bi/operational-insights` fortsat leverer den forklarbare incident risk score, som dashboardet viser i MVP'en.

## RabbitMQ Event Flow

Når `POST /api/telemetry` modtager et telemetry event, sker der tre ting:

```text
1. Eventet valideres og gemmes i PostgreSQL.
2. AnalyticsDomainService evaluerer eventet og gemmer eventuelle anomalies.
3. Backend publicerer en JSON-besked til RabbitMQ-køen telemetry.events.
```

RabbitMQ er ikke source of truth. Hvis en besked bruges af en senere worker,
alert-service eller integration, kan den læses asynkront uden at blokere API'et.
I MVP'en demonstrerer køen, hvordan Operational Monitoring kan udvides mod en
event-driven arkitektur uden at gøre dashboardet eller domænelogikken tungere.

## Microservice Ansvar

Telemetry Service (`localhost:8002` på VM, publiceret via gateway på `:8000/api/telemetry`) har ansvar for:

- `POST /api/telemetry`
- `GET /api/telemetry`
- validering af telemetry
- persistence i PostgreSQL
- anomaly detection ved ingestion
- publish af `telemetry.created` til RabbitMQ

Insights Service (`localhost:8001` på VM, publiceret via gateway på `:8000`) har ansvar for:

- `GET /dashboard`
- `GET /api/anomalies`
- `GET /api/insights/summary`
- `GET /api/insights/charger-health`
- `GET /api/insights/anomaly-rate`
- `GET /api/bi/operational-insights`
- read-only `GET /api/telemetry` til dashboardets live/trend views
- read-only `GET /api/dashboard/telemetry` til gateway/dashboard
- KPI'er, anomaly views og incident risk score

## API Endpoints

| Method | Endpoint | Beskrivelse |
| --- | --- | --- |
| GET | `:8000/api/health` | Tjekker den offentlige Insights/gateway-side |
| POST | `:8000/api/telemetry` | Gemmer et TelemetryEvent i Telemetry Service og evaluerer anomaly-regler |
| GET | `:8000/api/dashboard/telemetry` | Read-only telemetry til dashboard |
| GET | `:8000/api/anomalies` | Lister detekterede Anomalies |
| GET | `:8000/api/anomalies/{id}` | Henter én detekteret Anomaly |
| GET | `:8000/api/insights/summary` | Viser samlet operationel status |
| GET | `:8000/api/insights/charger-health` | Viser health state per Charger |
| GET | `:8000/api/insights/anomaly-rate` | Viser anomaly rate og severity distribution |
| GET | `:8000/api/bi/operational-insights` | Returnerer flade BI-ready records |
| GET | `localhost:8002/api/health` | Tjekker Telemetry Service direkte fra VM'en |
| GET | `localhost:8001/api/health` | Tjekker Insights Service direkte fra VM'en |

## Curl Eksempler Til Demo

Health check:

```bash
curl http://localhost:8000/api/health
curl http://localhost:8002/api/health
curl http://localhost:8001/api/health
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
3. Vis `GET :8000/api/telemetry`.
4. Vis `GET :8000/api/anomalies`.
5. Vis Operational Insights endpoints på `:8000`.
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

## GitHub Actions CI/CD

Repositoryet indeholder et simpelt CI/CD-workflow:

```text
.github/workflows/ci.yml
```

Workflowet kører tests på `push` og `pull_request`, installerer backend dependencies og kører `pytest`.

Når tests er grønne på `main`, deployer workflowet automatisk til VM'en via SSH:

```bash
cd /home/azureuser/voltedge
git pull --ff-only origin main
sudo docker compose up -d --build
```

GitHub Actions kræver disse repository secrets:

```text
VM_HOST
VM_USER
VM_SSH_KEY
```

Det er en simpel CD-løsning inden for MVP-scope. Den bruger ikke Kubernetes, Terraform eller container registry.
