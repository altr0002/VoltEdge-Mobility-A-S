from datetime import UTC, datetime

from app.infrastructure.models import TelemetryEventRecord
from app.infrastructure.rabbitmq_publisher import RabbitMQTelemetryPublisher


def _telemetry_record() -> TelemetryEventRecord:
    return TelemetryEventRecord(
        id=1,
        charger_id="CHG-001",
        connector_id="CONN-1",
        status="CHARGING",
        power_kw=42.5,
        error_code=None,
        heartbeat_at=datetime(2026, 5, 27, 10, 0, tzinfo=UTC),
        received_at=datetime(2026, 5, 27, 10, 1, tzinfo=UTC),
    )


def test_publisher_skips_when_disabled():
    publisher = RabbitMQTelemetryPublisher(
        rabbitmq_url="amqp://voltedge:voltedge@rabbitmq:5672/",
        enabled=False,
    )

    published = publisher.publish_telemetry_created(
        _telemetry_record(),
        anomaly_count=0,
    )

    assert published is False


def test_publisher_skips_when_url_is_missing():
    publisher = RabbitMQTelemetryPublisher(rabbitmq_url="", enabled=True)

    published = publisher.publish_telemetry_created(
        _telemetry_record(),
        anomaly_count=1,
    )

    assert published is False
