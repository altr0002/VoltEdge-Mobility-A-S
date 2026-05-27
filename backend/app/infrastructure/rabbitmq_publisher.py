import json
import logging
import os
from datetime import datetime
from typing import Any

import pika
from pika.exceptions import AMQPError

from app.infrastructure.models import TelemetryEventRecord


LOGGER = logging.getLogger(__name__)


class RabbitMQTelemetryPublisher:
    queue_name = "telemetry.events"

    def __init__(
        self,
        rabbitmq_url: str | None = None,
        enabled: bool | None = None,
    ) -> None:
        self.rabbitmq_url = rabbitmq_url or os.getenv("RABBITMQ_URL", "")
        self.enabled = enabled if enabled is not None else self._is_enabled()

    def publish_telemetry_created(
        self,
        telemetry_event: TelemetryEventRecord,
        anomaly_count: int,
    ) -> bool:
        if not self.enabled or not self.rabbitmq_url:
            return False

        message = {
            "event_type": "telemetry.created",
            "telemetry_event": {
                "id": telemetry_event.id,
                "charger_id": telemetry_event.charger_id,
                "connector_id": telemetry_event.connector_id,
                "status": telemetry_event.status,
                "power_kw": telemetry_event.power_kw,
                "error_code": telemetry_event.error_code,
                "heartbeat_at": self._to_isoformat(telemetry_event.heartbeat_at),
                "received_at": self._to_isoformat(telemetry_event.received_at),
            },
            "anomaly_count": anomaly_count,
        }

        try:
            connection = pika.BlockingConnection(
                pika.URLParameters(self.rabbitmq_url),
            )
            channel = connection.channel()
            channel.queue_declare(queue=self.queue_name, durable=True)
            channel.basic_publish(
                exchange="",
                routing_key=self.queue_name,
                body=json.dumps(message).encode("utf-8"),
                properties=pika.BasicProperties(
                    content_type="application/json",
                    delivery_mode=2,
                ),
            )
            connection.close()
            return True
        except AMQPError:
            LOGGER.exception("Could not publish telemetry event to RabbitMQ")
            return False

    @staticmethod
    def _is_enabled() -> bool:
        value = os.getenv("RABBITMQ_ENABLED", "true").lower()
        return value not in {"0", "false", "no", "off"}

    @staticmethod
    def _to_isoformat(value: Any) -> str | None:
        if value is None:
            return None

        if isinstance(value, datetime):
            return value.isoformat()

        return str(value)
