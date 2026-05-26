# Demo Script

## 1. Start the platform

```bash
docker compose up --build
```

## 2. Verify API health

```bash
curl http://localhost:8000/api/health
```

Expected result: the API returns `status: ok`.

## 3. Submit normal charger telemetry

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

## 4. Read stored telemetry

```bash
curl http://localhost:8000/api/telemetry
```

Use this response to show that the API validates operational telemetry and stores it in PostgreSQL.

## 5. Submit faulty charger telemetry

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

## 6. Read detected anomalies

```bash
curl http://localhost:8000/api/anomalies
```

Use this response to show the Sprint 2 flow: TelemetryEvent -> AnalyticsDomainService -> Anomaly -> GET /api/anomalies.
