from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.monitoring import AnomalyRateInsight, OperationalInsightSummary
from app.domain.services.analytics_domain_service import AnalyticsDomainService
from app.infrastructure.database import get_db
from app.infrastructure.models import AnomalyRecord, TelemetryEventRecord
from app.schemas.insights import (
    AnomalyRateInsightRead,
    ChargerHealthInsightRead,
    OperationalInsightSummaryRead,
)

router = APIRouter(prefix="/insights", tags=["Operational Insights"])


@router.get("/summary", response_model=OperationalInsightSummaryRead)
def get_operational_summary(
    db: Session = Depends(get_db),
) -> OperationalInsightSummary:
    telemetry_events = _list_telemetry_events(db)
    anomalies = _list_anomalies(db)

    return AnalyticsDomainService().calculate_summary(telemetry_events, anomalies)


@router.get("/charger-health", response_model=list[ChargerHealthInsightRead])
def get_charger_health(db: Session = Depends(get_db)):
    telemetry_events = _list_telemetry_events(db)
    anomalies = _list_anomalies(db)

    return AnalyticsDomainService().calculate_charger_health(
        telemetry_events,
        anomalies,
    )


@router.get("/anomaly-rate", response_model=AnomalyRateInsightRead)
def get_anomaly_rate(db: Session = Depends(get_db)) -> AnomalyRateInsight:
    telemetry_events = _list_telemetry_events(db)
    anomalies = _list_anomalies(db)

    return AnalyticsDomainService().calculate_anomaly_rate(telemetry_events, anomalies)


def _list_telemetry_events(db: Session) -> list[TelemetryEventRecord]:
    statement = select(TelemetryEventRecord)
    return list(db.scalars(statement).all())


def _list_anomalies(db: Session) -> list[AnomalyRecord]:
    statement = select(AnomalyRecord)
    return list(db.scalars(statement).all())
