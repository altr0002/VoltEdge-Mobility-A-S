from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.domain.monitoring import AnomalyRateInsight, OperationalInsightSummary
from app.domain.services.analytics_domain_service import AnalyticsDomainService
from app.infrastructure.database import get_db
from app.infrastructure.operational_data_repository import OperationalDataRepository
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
    operational_data = OperationalDataRepository(db)

    return AnalyticsDomainService().calculate_summary(
        operational_data.list_telemetry_events(),
        operational_data.list_anomalies(),
    )


@router.get("/charger-health", response_model=list[ChargerHealthInsightRead])
def get_charger_health(db: Session = Depends(get_db)):
    operational_data = OperationalDataRepository(db)

    return AnalyticsDomainService().calculate_charger_health(
        operational_data.list_telemetry_events(),
        operational_data.list_anomalies(),
    )


@router.get("/anomaly-rate", response_model=AnomalyRateInsightRead)
def get_anomaly_rate(db: Session = Depends(get_db)) -> AnomalyRateInsight:
    operational_data = OperationalDataRepository(db)

    return AnalyticsDomainService().calculate_anomaly_rate(
        operational_data.list_telemetry_events(),
        operational_data.list_anomalies(),
    )
