from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.monitoring import Heartbeat, PowerMeasurement, TelemetryEvent
from app.domain.services.analytics_domain_service import AnalyticsDomainService
from app.infrastructure.anomaly_repository import AnomalyRepository
from app.infrastructure.database import get_db
from app.infrastructure.models import TelemetryEventRecord
from app.schemas.telemetry import TelemetryEventCreate, TelemetryEventRead

router = APIRouter(prefix="/telemetry", tags=["Telemetry Monitoring"])


@router.post(
    "",
    response_model=TelemetryEventRead,
    status_code=status.HTTP_201_CREATED,
)
def create_telemetry_event(
    payload: TelemetryEventCreate,
    db: Session = Depends(get_db),
) -> TelemetryEventRecord:
    telemetry_event = TelemetryEventRecord(
        charger_id=payload.charger_id,
        connector_id=payload.connector_id,
        status=payload.status.value,
        power_kw=payload.power_kw,
        error_code=payload.error_code.value if payload.error_code else None,
        heartbeat_at=payload.heartbeat_at,
    )

    db.add(telemetry_event)
    db.commit()
    db.refresh(telemetry_event)

    domain_event = TelemetryEvent(
        id=telemetry_event.id,
        charger_id=payload.charger_id,
        connector_id=payload.connector_id,
        status=payload.status,
        power=PowerMeasurement(payload.power_kw),
        error_code=payload.error_code,
        heartbeat=Heartbeat(payload.heartbeat_at),
    )
    anomalies = AnalyticsDomainService().evaluate(domain_event)
    if anomalies:
        anomaly_repository = AnomalyRepository(db)
        anomaly_repository.add_many(anomalies)
        db.commit()

    return telemetry_event


@router.get("", response_model=list[TelemetryEventRead])
def list_telemetry_events(db: Session = Depends(get_db)) -> list[TelemetryEventRecord]:
    statement = select(TelemetryEventRecord).order_by(TelemetryEventRecord.received_at.desc())
    return list(db.scalars(statement).all())
