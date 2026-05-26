import argparse
import json
from datetime import UTC, datetime
from urllib import error, request


DEMO_EVENTS = [
    {
        "charger_id": "CHG-DEMO-HEALTHY",
        "connector_id": "CONN-1",
        "status": "CHARGING",
        "power_kw": 42.5,
        "error_code": None,
    },
    {
        "charger_id": "CHG-DEMO-WARNING",
        "connector_id": "CONN-1",
        "status": "CHARGING",
        "power_kw": 0,
        "error_code": None,
    },
    {
        "charger_id": "CHG-DEMO-CRITICAL",
        "connector_id": "CONN-1",
        "status": "FAULTED",
        "power_kw": 0,
        "error_code": "OVER_TEMPERATURE",
    },
    {
        "charger_id": "CHG-DEMO-OFFLINE",
        "connector_id": "CONN-1",
        "status": "OFFLINE",
        "power_kw": 0,
        "error_code": "COMMUNICATION_LOSS",
    },
    {
        "charger_id": "CHG-DEMO-UNAVAILABLE",
        "connector_id": "CONN-2",
        "status": "UNAVAILABLE",
        "power_kw": 0,
        "error_code": None,
    },
]


def post_json(url: str, payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with request.urlopen(req, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Seed VoltEdge demo telemetry through the public API.",
    )
    parser.add_argument(
        "--base-url",
        default="http://localhost:8000",
        help="Base URL for the running VoltEdge API.",
    )
    args = parser.parse_args()

    heartbeat_at = datetime.now(UTC).replace(microsecond=0).isoformat()
    telemetry_url = f"{args.base_url.rstrip('/')}/api/telemetry"

    for event in DEMO_EVENTS:
        payload = {**event, "heartbeat_at": heartbeat_at}
        try:
            created = post_json(telemetry_url, payload)
        except error.URLError as exc:
            raise SystemExit(f"Could not reach {telemetry_url}: {exc}") from exc

        print(
            f"Created telemetry event {created['id']} "
            f"for {created['charger_id']} ({created['status']})"
        )


if __name__ == "__main__":
    main()
