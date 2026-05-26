from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.domain.monitoring import AnomalySeverity, AnomalyType


class AnomalyRead(BaseModel):
    id: int
    telemetry_event_id: int
    charger_id: str
    connector_id: str
    anomaly_type: AnomalyType
    severity: AnomalySeverity
    description: str
    detected_at: datetime

    model_config = ConfigDict(from_attributes=True)
