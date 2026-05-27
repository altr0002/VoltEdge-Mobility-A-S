from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.api.anomalies import router as anomalies_router
from app.api.bi import router as bi_router
from app.api.health import router as health_router
from app.api.insights import router as insights_router
from app.api.telemetry_read import router as telemetry_read_router
from app.infrastructure import models
from app.infrastructure.database import Base, engine


STATIC_DIR = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="VoltEdge Insights Service",
    description="Read-side service for operational insights, anomalies and dashboard.",
    version="0.4.0",
    lifespan=lifespan,
)
app.state.service_name = "voltedge-insights-service"

app.include_router(health_router, prefix="/api")
app.include_router(telemetry_read_router, prefix="/api")
app.include_router(telemetry_read_router, prefix="/api/dashboard")
app.include_router(anomalies_router, prefix="/api")
app.include_router(insights_router, prefix="/api")
app.include_router(bi_router, prefix="/api")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def redirect_to_dashboard() -> RedirectResponse:
    return RedirectResponse(url="/dashboard")


@app.get("/dashboard", include_in_schema=False)
def get_dashboard() -> FileResponse:
    return FileResponse(STATIC_DIR / "dashboard.html")
