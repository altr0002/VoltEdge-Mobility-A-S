# Action Log: RabbitMQ Integration

Date: 2026-05-27

## 1. Baseline Before RabbitMQ

Before implementing RabbitMQ, GitHub and local tests were checked to confirm that the project was stable.

GitHub CLI authentication:

```text
Logged in to github.com account altr0002
Token scopes include repo and workflow
```

Latest GitHub Actions status before RabbitMQ:

```text
completed success Add CI and BI-ready reporting support
completed failure Add CI and BI-ready reporting support
completed success Finish exam MVP readiness
```

The latest run was successful, so the project had a green CI baseline before the RabbitMQ changes.

Local tests before RabbitMQ:

```text
20 passed
```

## 2. RabbitMQ Design Decision

RabbitMQ was implemented as a small integration queue inside the Operational Monitoring MVP.

The goal was not to replace PostgreSQL or make the system complex. PostgreSQL remains the source of truth. RabbitMQ is used to publish a lightweight event after telemetry has been accepted and stored.

Chosen event:

```text
event_type: telemetry.created
queue: telemetry.events
```

Reasoning:

- The API should still validate and persist telemetry synchronously.
- The existing anomaly detection flow should remain simple.
- RabbitMQ should demonstrate event-driven architecture without adding a full worker pipeline.
- A future alert service, notification service or analytics worker could consume the queue.

## 3. Docker Compose Changes

RabbitMQ was added as a third Docker Compose service:

```text
backend
postgres
rabbitmq
```

RabbitMQ image:

```text
rabbitmq:3.13-management-alpine
```

Ports:

```text
5672  AMQP
15672 Management UI
```

Credentials:

```text
user: voltedge
password: voltedge
```

The backend now waits for both PostgreSQL and RabbitMQ to become healthy before starting.

## 4. Backend Changes

The backend dependency `pika==1.3.2` was added.

A new infrastructure component was added:

```text
app/infrastructure/rabbitmq_publisher.py
```

The publisher creates durable messages on the queue:

```text
telemetry.events
```

The telemetry API now performs this sequence:

```text
1. Receive POST /api/telemetry
2. Validate payload with Pydantic
3. Store TelemetryEvent in PostgreSQL
4. Run AnalyticsDomainService anomaly detection
5. Store generated Anomaly records in PostgreSQL
6. Publish telemetry.created message to RabbitMQ
7. Return the stored telemetry response
```

The RabbitMQ publish step is deliberately non-critical. If RabbitMQ is disabled or not configured in local test environments, the publisher skips publishing. This keeps the test suite simple and avoids requiring RabbitMQ for unit/API tests.

## 5. Tests Added

Tests were added for RabbitMQ publisher behavior:

```text
tests/test_rabbitmq_publisher.py
```

The tests verify:

- publishing is skipped when RabbitMQ is disabled
- publishing is skipped when no RabbitMQ URL is configured

Local test result after RabbitMQ:

```text
22 passed
```

## 6. Docker Compose Validation

Docker Compose configuration was validated after adding RabbitMQ.

Expected services:

```text
backend
postgres
rabbitmq
```

Expected backend environment:

```text
DATABASE_URL=postgresql+psycopg2://voltedge:voltedge@postgres:5432/voltedge_monitoring
RABBITMQ_URL=amqp://voltedge:voltedge@rabbitmq:5672/
RABBITMQ_ENABLED=true
```

## 7. VM Deployment

Updated project files were copied to the VM:

```text
/home/azureuser/voltedge
```

The VM Docker Compose stack was rebuilt:

```bash
sudo docker compose up -d --build
```

RabbitMQ image was pulled on the VM and the backend image was rebuilt with the new `pika` dependency.

VM services after deployment:

```text
voltedge-backend-1   Up
voltedge-postgres-1  Up (healthy)
voltedge-rabbitmq-1  Up (healthy)
```

## 8. Runtime Verification On VM

API health was checked:

```text
{"status":"ok","service":"voltedge-operational-monitoring"}
```

A new telemetry event was posted:

```text
charger_id: CHG-RABBITMQ-DEMO
status: CHARGING
power_kw: 35.5
```

RabbitMQ queue verification:

```text
name              messages_ready  messages_unacknowledged
telemetry.events 1               0
```

RabbitMQ Management API confirmed:

```text
queue: telemetry.events
state: running
messages: 1
messages_ready: 1
messages_persistent: 1
publish: 1
```

## 9. Management UI Access

RabbitMQ Management UI works internally on the VM:

```text
http://localhost:15672
```

The public VM IP does not expose port 15672 directly. This is acceptable and safer. Use an SSH tunnel from the Mac:

```bash
ssh -L 15672:localhost:15672 VMVoltEdge
```

Then open:

```text
http://localhost:15672
```

## 10. Scope Explanation

RabbitMQ is now inside the MVP as a small event-driven extension.

It supports the assignment because it demonstrates how telemetry ingestion can be decoupled from future consumers such as alerting, notifications or background analytics.

It remains within scope because:

- PostgreSQL is still the primary database.
- No full worker system was added.
- No Kafka/event streaming platform was introduced.
- Dashboard and API reads still use the existing Operational Monitoring endpoints.
- The implementation is easy to explain and test.

Final architecture:

```text
Charger / Simulator
  -> FastAPI telemetry API
  -> PostgreSQL telemetry_events
  -> AnalyticsDomainService
  -> PostgreSQL anomalies
  -> RabbitMQ telemetry.events
  -> Dashboard / API insights
```
