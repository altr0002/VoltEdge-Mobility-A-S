from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

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
    anomalies: Mapped[list["AnomalyRecord"]] = relationship(
        back_populates="telemetry_event",
        cascade="all, delete-orphan",
    )


class AnomalyRecord(Base):
    __tablename__ = "anomalies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    telemetry_event_id: Mapped[int] = mapped_column(
        ForeignKey("telemetry_events.id"),
        nullable=False,
        index=True,
    )
    charger_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    connector_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    anomaly_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )
    telemetry_event: Mapped[TelemetryEventRecord] = relationship(
        back_populates="anomalies",
    )
