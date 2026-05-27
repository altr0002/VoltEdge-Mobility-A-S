from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.telemetry import router as telemetry_router
from app.infrastructure.database import Base, engine
from app.infrastructure import models


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="VoltEdge Telemetry Service",
    description="Telemetry ingestion service for EV charger operational data.",
    version="0.4.0",
    lifespan=lifespan,
)
app.state.service_name = "voltedge-telemetry-service"

app.include_router(health_router, prefix="/api")
app.include_router(telemetry_router, prefix="/api")
