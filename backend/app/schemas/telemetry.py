from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.domain.monitoring import ChargerStatus, ErrorCode


class TelemetryEventCreate(BaseModel):
    charger_id: str = Field(..., min_length=1, max_length=64, examples=["CHG-001"])
    connector_id: str = Field(..., min_length=1, max_length=64, examples=["CONN-1"])
    status: ChargerStatus = Field(..., examples=[ChargerStatus.CHARGING])
    power_kw: float = Field(..., ge=0, le=350, examples=[42.5])
    error_code: ErrorCode | None = Field(default=None, examples=[None])
    heartbeat_at: datetime = Field(..., examples=["2026-05-25T10:15:00Z"])


class TelemetryEventRead(TelemetryEventCreate):
    id: int
    received_at: datetime

    model_config = ConfigDict(from_attributes=True)
