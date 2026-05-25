from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database import Base


class TelemetryEventRecord(Base):
    __tablename__ = "telemetry_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    charger_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    connector_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    power_kw: Mapped[float] = mapped_column(Float, nullable=False)
    error_code: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    heartbeat_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
