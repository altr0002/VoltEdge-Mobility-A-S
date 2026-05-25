import os

os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"

import pytest
from fastapi.testclient import TestClient

from app.infrastructure.database import Base, engine
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_health_endpoint_returns_ok():
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_and_list_telemetry_events():
    payload = {
        "charger_id": "CHG-001",
        "connector_id": "CONN-1",
        "status": "CHARGING",
        "power_kw": 42.5,
        "error_code": None,
        "heartbeat_at": "2026-05-25T10:15:00Z",
    }

    create_response = client.post("/api/telemetry", json=payload)

    assert create_response.status_code == 201
    created_event = create_response.json()
    assert created_event["id"] == 1
    assert created_event["charger_id"] == "CHG-001"
    assert created_event["status"] == "CHARGING"

    list_response = client.get("/api/telemetry")

    assert list_response.status_code == 200
    stored_events = list_response.json()
    assert len(stored_events) == 1
    assert stored_events[0]["connector_id"] == "CONN-1"
    assert stored_events[0]["power_kw"] == 42.5


def test_rejects_invalid_power_measurement():
    payload = {
        "charger_id": "CHG-001",
        "connector_id": "CONN-1",
        "status": "CHARGING",
        "power_kw": -1,
        "error_code": None,
        "heartbeat_at": "2026-05-25T10:15:00Z",
    }

    response = client.post("/api/telemetry", json=payload)

    assert response.status_code == 422
