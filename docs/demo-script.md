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

## 3. Submit charger telemetry

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

Use this response to show that the API validates operational telemetry, stores it in PostgreSQL and exposes BI-ready event data for later analytics.
