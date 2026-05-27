from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.infrastructure.models import TelemetryEventRecord
from app.schemas.telemetry import TelemetryEventRead

router = APIRouter(prefix="/telemetry", tags=["Telemetry Read Model"])


@router.get("", response_model=list[TelemetryEventRead])
def list_telemetry_events(db: Session = Depends(get_db)) -> list[TelemetryEventRecord]:
    statement = select(TelemetryEventRecord).order_by(
        TelemetryEventRecord.received_at.desc(),
    )
    return list(db.scalars(statement).all())
