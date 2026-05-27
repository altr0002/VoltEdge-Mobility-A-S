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
    charger_id: str,
    status: str,
    power_kw: float,
    error_code: str | None = None,
):
    payload = {
        "charger_id": charger_id,
        "connector_id": "CONN-1",
        "status": status,
        "power_kw": power_kw,
        "error_code": error_code,
        "heartbeat_at": "2026-05-25T10:15:00Z",
    }

    return telemetry_client.post("/api/telemetry", json=payload)


def test_summary_handles_zero_telemetry_events():
    response = insights_client.get("/api/insights/summary")

    assert response.status_code == 200
    assert response.json() == {
        "total_telemetry_events": 0,
        "total_anomalies": 0,
        "chargers_with_anomalies": 0,
        "faulted_chargers": 0,
        "average_power_kw": 0.0,
        "anomaly_rate_percent": 0.0,
        "top_problematic_chargers": [],
    }


def test_summary_returns_operational_insights():
    _post_telemetry("CHG-001", "CHARGING", 42.5)
    _post_telemetry("CHG-002", "FAULTED", 0)
    _post_telemetry("CHG-003", "CHARGING", 0)

    response = insights_client.get("/api/insights/summary")

    assert response.status_code == 200
    summary = response.json()
    assert summary["total_telemetry_events"] == 3
    assert summary["total_anomalies"] == 2
    assert summary["chargers_with_anomalies"] == 2
    assert summary["faulted_chargers"] == 1
    assert summary["average_power_kw"] == 14.17
    assert summary["anomaly_rate_percent"] == 66.67
    assert summary["top_problematic_chargers"] == [
        {"charger_id": "CHG-002", "total_anomalies": 1},
        {"charger_id": "CHG-003", "total_anomalies": 1},
    ]


def test_charger_health_returns_health_state_per_charger():
    _post_telemetry("CHG-001", "CHARGING", 42.5)
    _post_telemetry("CHG-002", "FAULTED", 0)
    _post_telemetry("CHG-003", "CHARGING", 0)
    _post_telemetry("CHG-004", "UNAVAILABLE", 0)
    _post_telemetry("CHG-005", "OFFLINE", 0)

    response = insights_client.get("/api/insights/charger-health")

    assert response.status_code == 200
    health_by_charger = {
        charger["charger_id"]: charger
        for charger in response.json()
    }
    assert health_by_charger["CHG-001"]["health_state"] == "HEALTHY"
    assert health_by_charger["CHG-001"]["total_anomalies"] == 0
    assert health_by_charger["CHG-002"]["health_state"] == "CRITICAL"
    assert health_by_charger["CHG-002"]["high_severity_anomalies"] == 1
    assert health_by_charger["CHG-003"]["health_state"] == "WARNING"
    assert health_by_charger["CHG-003"]["latest_status"] == "CHARGING"
    assert health_by_charger["CHG-004"]["health_state"] == "WARNING"
    assert health_by_charger["CHG-004"]["latest_status"] == "UNAVAILABLE"
    assert health_by_charger["CHG-005"]["health_state"] == "CRITICAL"
    assert health_by_charger["CHG-005"]["latest_status"] == "OFFLINE"


def test_anomaly_rate_returns_rate_and_severity_distribution():
    _post_telemetry("CHG-001", "CHARGING", 42.5)
    _post_telemetry("CHG-002", "FAULTED", 0)
    _post_telemetry("CHG-003", "CHARGING", 0)

    response = insights_client.get("/api/insights/anomaly-rate")

    assert response.status_code == 200
    assert response.json() == {
        "total_telemetry_events": 3,
        "total_anomalies": 2,
        "anomaly_rate_percent": 66.67,
        "severity_distribution": {
            "HIGH": 1,
            "MEDIUM": 1,
        },
    }


def test_bi_operational_insights_returns_flat_power_bi_ready_records():
    _post_telemetry("CHG-001", "CHARGING", 42.5)
    _post_telemetry("CHG-002", "FAULTED", 0, "OVER_TEMPERATURE")
    _post_telemetry("CHG-003", "CHARGING", 0)

    response = insights_client.get("/api/bi/operational-insights")

    assert response.status_code == 200
    records = {
        record["charger_id"]: record
        for record in response.json()
    }
    assert records["CHG-001"] == {
        "charger_id": "CHG-001",
        "latest_status": "CHARGING",
        "total_events": 1,
        "total_anomalies": 0,
        "high_severity_anomalies": 0,
        "average_power_kw": 42.5,
        "anomaly_rate_percent": 0.0,
        "incident_risk_score": 0,
        "incident_risk_level": "LOW",
        "health_state": "HEALTHY",
    }
    assert records["CHG-002"]["latest_status"] == "FAULTED"
    assert records["CHG-002"]["total_anomalies"] == 2
    assert records["CHG-002"]["high_severity_anomalies"] == 2
    assert records["CHG-002"]["anomaly_rate_percent"] == 200.0
    assert records["CHG-002"]["incident_risk_score"] == 100
    assert records["CHG-002"]["incident_risk_level"] == "HIGH"
    assert records["CHG-002"]["health_state"] == "CRITICAL"
    assert records["CHG-003"]["total_anomalies"] == 1
    assert records["CHG-003"]["anomaly_rate_percent"] == 100.0
    assert records["CHG-003"]["incident_risk_score"] == 53
    assert records["CHG-003"]["incident_risk_level"] == "MEDIUM"
    assert records["CHG-003"]["health_state"] == "WARNING"


def test_bi_operational_insights_handles_zero_telemetry_events():
    response = insights_client.get("/api/bi/operational-insights")

    assert response.status_code == 200
    assert response.json() == []


def test_insights_service_serves_dashboard_and_read_only_telemetry():
    _post_telemetry("CHG-001", "CHARGING", 42.5)

    dashboard_response = insights_client.get("/dashboard")
    telemetry_response = insights_client.get("/api/telemetry")
    dashboard_telemetry_response = insights_client.get("/api/dashboard/telemetry")

    assert dashboard_response.status_code == 200
    assert "VoltEdge Dashboard" in dashboard_response.text
    assert telemetry_response.status_code == 200
    assert dashboard_telemetry_response.status_code == 200
    assert telemetry_response.json()[0]["charger_id"] == "CHG-001"


def test_insights_service_does_not_accept_telemetry_writes():
    response = insights_client.post(
        "/api/telemetry",
        json={
            "charger_id": "CHG-001",
            "connector_id": "CONN-1",
            "status": "CHARGING",
            "power_kw": 42.5,
            "error_code": None,
            "heartbeat_at": "2026-05-25T10:15:00Z",
        },
    )

    assert response.status_code == 405
