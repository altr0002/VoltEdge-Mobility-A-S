CREATE TABLE IF NOT EXISTS telemetry_events (
    id SERIAL PRIMARY KEY,
    charger_id VARCHAR(64) NOT NULL,
    connector_id VARCHAR(64) NOT NULL,
    status VARCHAR(32) NOT NULL,
    power_kw NUMERIC(8, 3) NOT NULL CHECK (power_kw >= 0),
    error_code VARCHAR(64),
    heartbeat_at TIMESTAMPTZ NOT NULL,
    received_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_telemetry_events_charger_id
    ON telemetry_events (charger_id);

CREATE INDEX IF NOT EXISTS idx_telemetry_events_connector_id
    ON telemetry_events (connector_id);

CREATE INDEX IF NOT EXISTS idx_telemetry_events_status
    ON telemetry_events (status);

CREATE INDEX IF NOT EXISTS idx_telemetry_events_received_at
    ON telemetry_events (received_at DESC);
