from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.infrastructure.anomaly_repository import AnomalyRepository
from app.infrastructure.database import get_db
from app.infrastructure.models import AnomalyRecord
from app.schemas.anomaly import AnomalyRead

router = APIRouter(prefix="/anomalies", tags=["Anomaly Detection"])


@router.get("", response_model=list[AnomalyRead])
def list_anomalies(db: Session = Depends(get_db)) -> list[AnomalyRecord]:
    return AnomalyRepository(db).list_all()


@router.get("/{anomaly_id}", response_model=AnomalyRead)
def get_anomaly(anomaly_id: int, db: Session = Depends(get_db)) -> AnomalyRecord:
    anomaly = AnomalyRepository(db).get_by_id(anomaly_id)
    if anomaly is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Anomaly not found",
        )

    return anomaly
