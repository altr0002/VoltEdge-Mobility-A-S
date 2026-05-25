# API Examples

## Health

```bash
curl http://localhost:8000/api/health
```

## Create TelemetryEvent

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

## List TelemetryEvents

```bash
curl http://localhost:8000/api/telemetry
```

## Example With ErrorCode

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
