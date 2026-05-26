from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.domain.monitoring import BiOperationalInsight
from app.domain.services.analytics_domain_service import AnalyticsDomainService
from app.infrastructure.database import get_db
from app.infrastructure.operational_data_repository import OperationalDataRepository
from app.schemas.insights import BiOperationalInsightRead

router = APIRouter(prefix="/bi", tags=["BI Ready Data"])


@router.get("/operational-insights", response_model=list[BiOperationalInsightRead])
def get_bi_operational_insights(
    db: Session = Depends(get_db),
) -> list[BiOperationalInsight]:
    operational_data = OperationalDataRepository(db)

    return AnalyticsDomainService().calculate_bi_operational_insights(
        operational_data.list_telemetry_events(),
        operational_data.list_anomalies(),
    )
