from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.models import AnomalyRecord, TelemetryEventRecord


class OperationalDataRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_telemetry_events(self) -> list[TelemetryEventRecord]:
        statement = select(TelemetryEventRecord)
        return list(self.db.scalars(statement).all())

    def list_anomalies(self) -> list[AnomalyRecord]:
        statement = select(AnomalyRecord)
        return list(self.db.scalars(statement).all())
