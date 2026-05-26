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

CREATE TABLE IF NOT EXISTS anomalies (
    id SERIAL PRIMARY KEY,
    telemetry_event_id INTEGER NOT NULL REFERENCES telemetry_events(id),
    charger_id VARCHAR(64) NOT NULL,
    connector_id VARCHAR(64) NOT NULL,
    anomaly_type VARCHAR(64) NOT NULL,
    severity VARCHAR(16) NOT NULL,
    description VARCHAR(255) NOT NULL,
    detected_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_anomalies_telemetry_event_id
    ON anomalies (telemetry_event_id);

CREATE INDEX IF NOT EXISTS idx_anomalies_charger_id
    ON anomalies (charger_id);

CREATE INDEX IF NOT EXISTS idx_anomalies_connector_id
    ON anomalies (connector_id);

CREATE INDEX IF NOT EXISTS idx_anomalies_anomaly_type
    ON anomalies (anomaly_type);

CREATE INDEX IF NOT EXISTS idx_anomalies_severity
    ON anomalies (severity);

CREATE INDEX IF NOT EXISTS idx_anomalies_detected_at
    ON anomalies (detected_at DESC);
