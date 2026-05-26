from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.monitoring import Anomaly
from app.infrastructure.models import AnomalyRecord


class AnomalyRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def add_many(self, anomalies: list[Anomaly]) -> list[AnomalyRecord]:
        records = [
            AnomalyRecord(
                telemetry_event_id=anomaly.telemetry_event_id,
                charger_id=anomaly.charger_id,
                connector_id=anomaly.connector_id,
                anomaly_type=anomaly.anomaly_type.value,
                severity=anomaly.severity.value,
                description=anomaly.description,
                detected_at=anomaly.detected_at,
            )
            for anomaly in anomalies
        ]

        self.db.add_all(records)
        return records

    def list_all(self) -> list[AnomalyRecord]:
        statement = select(AnomalyRecord).order_by(AnomalyRecord.detected_at.desc())
        return list(self.db.scalars(statement).all())

    def get_by_id(self, anomaly_id: int) -> AnomalyRecord | None:
        return self.db.get(AnomalyRecord, anomaly_id)
