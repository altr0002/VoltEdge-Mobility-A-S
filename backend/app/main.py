from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.anomalies import router as anomalies_router
from app.api.health import router as health_router
from app.api.telemetry import router as telemetry_router
from app.infrastructure.database import Base, engine
from app.infrastructure import models


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="VoltEdge Operational Monitoring API",
    description="Telemetry monitoring and anomaly detection API for EV charger operations.",
    version="0.2.0",
    lifespan=lifespan,
)

app.include_router(health_router, prefix="/api")
app.include_router(telemetry_router, prefix="/api")
app.include_router(anomalies_router, prefix="/api")
