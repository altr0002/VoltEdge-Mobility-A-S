import os

os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"

import pytest
from fastapi.testclient import TestClient

from app.infrastructure.database import Base, engine
from app.insights_main import app as insights_app
from app.main import app as telemetry_app

insights_client = TestClient(insights_app)
telemetry_client = TestClient(telemetry_app)


@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def _post_telemetry(
    status: str,
    power_kw: float,
    error_code: str | None = None,
):
    payload = {
        "charger_id": "CHG-001",
        "connector_id": "CONN-1",
        "status": status,
        "power_kw": power_kw,
        "error_code": error_code,
        "heartbeat_at": "2026-05-25T10:15:00Z",
    }

    return telemetry_client.post("/api/telemetry", json=payload)


def test_normal_telemetry_event_does_not_create_anomaly():
    response = _post_telemetry("CHARGING", 42.5)

    assert response.status_code == 201

    anomalies_response = insights_client.get("/api/anomalies")

    assert anomalies_response.status_code == 200
    assert anomalies_response.json() == []


def test_faulted_telemetry_event_creates_anomaly():
    response = _post_telemetry("FAULTED", 0)

    assert response.status_code == 201

    anomalies = insights_client.get("/api/anomalies").json()
    assert len(anomalies) == 1
    assert anomalies[0]["anomaly_type"] == "CHARGER_FAULT"
    assert anomalies[0]["severity"] == "HIGH"
    assert anomalies[0]["description"] == "Charger reported FAULTED status."


def test_error_code_creates_anomaly():
    response = _post_telemetry("CHARGING", 20, "OVER_TEMPERATURE")

    assert response.status_code == 201

    anomalies = insights_client.get("/api/anomalies").json()
    assert len(anomalies) == 1
    assert anomalies[0]["anomaly_type"] == "ERROR_CODE_DETECTED"
    assert anomalies[0]["severity"] == "HIGH"


def test_charging_with_zero_power_creates_power_anomaly():
    response = _post_telemetry("CHARGING", 0)

    assert response.status_code == 201

    anomalies = insights_client.get("/api/anomalies").json()
    assert len(anomalies) == 1
    assert anomalies[0]["anomaly_type"] == "POWER_ANOMALY"
    assert anomalies[0]["severity"] == "MEDIUM"


def test_get_anomalies_returns_stored_anomalies():
    _post_telemetry("FAULTED", 0)
    _post_telemetry("CHARGING", 0)

    response = insights_client.get("/api/anomalies")

    assert response.status_code == 200
    anomalies = response.json()
    assert len(anomalies) == 2
    assert {anomaly["anomaly_type"] for anomaly in anomalies} == {
        "CHARGER_FAULT",
        "POWER_ANOMALY",
    }


def test_telemetry_service_does_not_expose_anomaly_read_model():
    response = telemetry_client.get("/api/anomalies")

    assert response.status_code == 404
