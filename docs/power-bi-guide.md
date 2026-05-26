# Power BI Guide

VoltEdge Operational Monitoring exposes BI-ready analytics data through the backend API. Power BI is treated as an independent visualization layer, while FastAPI and PostgreSQL remain the operational system.

The MVP does not include a `.pbix` file or embedded dashboard. Power BI can connect to the API as a web data source.

## BI Endpoint

Use this endpoint:

```text
http://<VM-IP>:8000/api/bi/operational-insights
```

From inside the VM:

```bash
curl http://localhost:8000/api/bi/operational-insights
```

The endpoint returns a flat list of records with:

- `charger_id`
- `latest_status`
- `total_events`
- `total_anomalies`
- `high_severity_anomalies`
- `average_power_kw`
- `anomaly_rate_percent`
- `health_state`

## Suggested Power BI Connection

1. Start the backend and PostgreSQL on the virtual machine with Docker Compose.
2. Confirm the API is reachable at `http://<VM-IP>:8000/docs`.
3. In Power BI Desktop, choose Get Data.
4. Choose Web.
5. Enter `http://<VM-IP>:8000/api/bi/operational-insights`.
6. Load the returned JSON as a table.

## Suggested Dashboard Visuals

- Total telemetry events
- Total anomalies
- Anomaly rate
- Charger health by `health_state`
- Top problematic chargers
- Average `power_kw`

## Scope

The dashboard itself is outside the backend code. The purpose of this MVP is to demonstrate that the backend exposes analytics-ready data that a BI tool can consume.
