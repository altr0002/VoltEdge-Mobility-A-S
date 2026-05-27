# Demo Script

## 1. SSH into the virtual machine

```bash
ssh <user>@<VM-IP>
```

## 2. Pull the newest code

```bash
cd ~/voltedge
git pull
```

If the VM project folder was copied manually instead of cloned with Git, copy the newest repository files to the VM before running the Docker Compose commands.

## 3. Start the platform on the VM

```bash
docker compose up -d --build
```

## 4. Check containers

```bash
docker compose ps
```

Expected services:

```text
backend
postgres
rabbitmq
```

## 5. Verify API health from inside the VM

```bash
curl http://localhost:8000/api/health
```

Expected result: the API returns `status: ok`.

## 6. Open Swagger from browser

```text
http://<VM-IP>:8000/docs
```

Open the operational dashboard:

```text
http://<VM-IP>:8000/dashboard
```

Open RabbitMQ Management UI through an SSH tunnel:

```bash
ssh -L 15672:localhost:15672 VMVoltEdge
```

Keep the SSH session open, then open:

```text
http://localhost:15672
```

Login:

```text
user: voltedge
password: voltedge
```

## 7. Submit normal charger telemetry

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

## 8. Read stored telemetry

```bash
curl http://localhost:8000/api/telemetry
```

Use this response to show that the API validates operational telemetry and stores it in PostgreSQL.

Also show that telemetry events are published to RabbitMQ:

1. Open `http://localhost:15672` through the SSH tunnel.
2. Go to Queues.
3. Open `telemetry.events`.
4. Confirm that messages have been published after `POST /api/telemetry`.

## 9. Submit faulty charger telemetry

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

## 10. Read detected anomalies

```bash
curl http://localhost:8000/api/anomalies
```

Use this response to show the flow: TelemetryEvent -> AnalyticsDomainService -> Anomaly -> GET /api/anomalies.

## 11. Read operational insights

```bash
curl http://localhost:8000/api/insights/summary
```

```bash
curl http://localhost:8000/api/insights/charger-health
```

```bash
curl http://localhost:8000/api/insights/anomaly-rate
```

Use these responses to show the full MVP value chain: Telemetry Monitoring -> Anomaly Detection -> Operational Insights.

Use the dashboard to show the same value chain visually:

```text
http://<VM-IP>:8000/dashboard
```

## 12. Read BI-ready data

```bash
curl http://localhost:8000/api/bi/operational-insights
```

Use this response to explain how Power BI can consume a flat API dataset as a web data source.

## Optional: Seed demo data

After Docker Compose is running, seed a small demo dataset:

```bash
python3 scripts/seed_demo_data.py
```

Then repeat the anomaly, insights and BI-ready endpoint calls.

## Optional: Simulate Power BI demo data

For a richer Power BI dashboard, create a larger telemetry history through the
VM API:

```bash
python3 scripts/simulate_demo_data.py --base-url http://<VM-IP>:8000
```

This creates multiple charger patterns over several days, including healthy
chargers, low power output, offline periods, unavailable windows, connector
failures and thermal faults. The simulator only submits telemetry. The backend
still performs validation, persistence, anomaly detection and BI-ready insight
calculation.

Use the BI endpoint from Power BI:

```text
http://<VM-IP>:8000/api/bi/operational-insights
```

Useful visuals:

- Top chargers by `incident_risk_score`
- Charger count by `incident_risk_level`
- Charger count by `health_state`
- `total_anomalies` by `charger_id`
- `average_power_kw` by `charger_id`
