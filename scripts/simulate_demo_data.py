import argparse
import json
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from random import Random
from urllib import error, request


DEFAULT_BASE_URL = "http://20.199.170.149:8000"


@dataclass(frozen=True)
class ChargerScenario:
    charger_id: str
    connector_id: str
    pattern: str
    base_power_kw: float


SCENARIOS = [
    ChargerScenario("CHG-FLEET-001", "CONN-1", "healthy", 44.0),
    ChargerScenario("CHG-FLEET-002", "CONN-1", "healthy", 38.0),
    ChargerScenario("CHG-FLEET-003", "CONN-1", "low_power", 31.0),
    ChargerScenario("CHG-HIGHWAY-001", "CONN-1", "thermal_fault", 120.0),
    ChargerScenario("CHG-HIGHWAY-002", "CONN-1", "offline_flaky", 95.0),
    ChargerScenario("CHG-DEPOT-001", "CONN-2", "connector_failure", 22.0),
    ChargerScenario("CHG-DEPOT-002", "CONN-2", "unavailable_window", 18.0),
    ChargerScenario("CHG-CITY-001", "CONN-1", "power_meter_issue", 36.0),
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


def build_event(
    scenario: ChargerScenario,
    heartbeat_at: datetime,
    step: int,
    last_step: int,
    rng: Random,
) -> dict:
    status = "CHARGING"
    power_kw = max(0, scenario.base_power_kw + rng.uniform(-6, 6))
    error_code = None

    hour = heartbeat_at.hour
    if hour < 5:
        status = "AVAILABLE"
        power_kw = 0

    if scenario.pattern == "low_power" and step % 9 == 0:
        status = "CHARGING"
        power_kw = 0

    if scenario.pattern == "thermal_fault" and step >= last_step - 4:
        status = "FAULTED"
        power_kw = 0
        error_code = "OVER_TEMPERATURE"

    if scenario.pattern == "offline_flaky" and step % 11 in {0, 1}:
        status = "OFFLINE"
        power_kw = 0
        error_code = "COMMUNICATION_LOSS"

    if scenario.pattern == "connector_failure" and step % 13 == 0:
        status = "FAULTED"
        power_kw = 0
        error_code = "CONNECTOR_LOCK_FAILURE"

    if scenario.pattern == "unavailable_window" and step % 16 in {5, 6, 7}:
        status = "UNAVAILABLE"
        power_kw = 0

    if scenario.pattern == "power_meter_issue" and step % 10 == 3:
        status = "CHARGING"
        power_kw = 0
        error_code = "POWER_METER_FAILURE"

    return {
        "charger_id": scenario.charger_id,
        "connector_id": scenario.connector_id,
        "status": status,
        "power_kw": round(power_kw, 2),
        "error_code": error_code,
        "heartbeat_at": heartbeat_at.isoformat(),
    }


def build_events(days: int, interval_hours: int) -> list[dict]:
    rng = Random(42)
    end_at = datetime.now(UTC).replace(minute=0, second=0, microsecond=0)
    start_at = end_at - timedelta(days=days)
    timestamps = []
    current = start_at

    while current <= end_at:
        timestamps.append(current)
        current += timedelta(hours=interval_hours)

    events: list[dict] = []
    last_step = len(timestamps) - 1
    for step, heartbeat_at in enumerate(timestamps):
        for scenario in SCENARIOS:
            events.append(
                build_event(
                    scenario=scenario,
                    heartbeat_at=heartbeat_at,
                    step=step,
                    last_step=last_step,
                    rng=rng,
                )
            )

    return events


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Simulate realistic VoltEdge telemetry by posting events to the public API."
        ),
    )
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help="Base URL for the running VoltEdge API. Defaults to the VM endpoint.",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Number of days of telemetry history to create.",
    )
    parser.add_argument(
        "--interval-hours",
        type=int,
        default=6,
        help="Hours between generated telemetry events.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the number of generated events without posting them.",
    )
    args = parser.parse_args()

    if args.days < 1:
        raise SystemExit("--days must be at least 1")
    if args.interval_hours < 1:
        raise SystemExit("--interval-hours must be at least 1")

    events = build_events(args.days, args.interval_hours)
    telemetry_url = f"{args.base_url.rstrip('/')}/api/telemetry"

    if args.dry_run:
        print(f"Would post {len(events)} telemetry events to {telemetry_url}")
        return

    created_count = 0
    for event in events:
        try:
            post_json(telemetry_url, event)
        except error.URLError as exc:
            raise SystemExit(f"Could not reach {telemetry_url}: {exc}") from exc
        created_count += 1

    print(f"Created {created_count} telemetry events at {telemetry_url}")


if __name__ == "__main__":
    main()
