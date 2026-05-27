const refreshButton = document.getElementById("refreshButton");
const apiStatus = document.getElementById("apiStatus");
const lastUpdated = document.getElementById("lastUpdated");

const numberFormat = new Intl.NumberFormat("en-US");
const decimalFormat = new Intl.NumberFormat("en-US", {
  minimumFractionDigits: 1,
  maximumFractionDigits: 1,
});

async function fetchJson(path) {
  const response = await fetch(path, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`${path} returned ${response.status}`);
  }
  return response.json();
}

function setText(id, value) {
  document.getElementById(id).textContent = value;
}

function riskClass(level) {
  return String(level || "").toLowerCase();
}

function statusClass(value) {
  return String(value || "").toLowerCase();
}

function formatDate(value) {
  if (!value) {
    return "";
  }
  return new Date(value).toLocaleString("en-GB", {
    day: "2-digit",
    month: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function renderKpis(summary) {
  setText("totalEvents", numberFormat.format(summary.total_telemetry_events));
  setText("totalAnomalies", numberFormat.format(summary.total_anomalies));
  setText("anomalyRate", `${decimalFormat.format(summary.anomaly_rate_percent)}%`);
  setText("faultedChargers", numberFormat.format(summary.faulted_chargers));
  setText("averagePower", `${decimalFormat.format(summary.average_power_kw)} kW`);
}

function renderRiskChart(records) {
  const root = document.getElementById("riskChart");
  const topRecords = [...records]
    .sort((a, b) => b.incident_risk_score - a.incident_risk_score)
    .slice(0, 8);

  if (topRecords.length === 0) {
    root.innerHTML = '<div class="empty">No charger data</div>';
    return;
  }

  root.innerHTML = topRecords
    .map((record) => {
      const score = Math.max(0, Math.min(100, record.incident_risk_score));
      const level = riskClass(record.incident_risk_level);
      return `
        <div class="bar-row">
          <div class="bar-label" title="${record.charger_id}">${record.charger_id}</div>
          <div class="bar-track">
            <div class="bar-fill ${level}" style="width: ${score}%"></div>
          </div>
          <div class="bar-value">${score}</div>
        </div>
      `;
    })
    .join("");
}

function countBy(records, field) {
  return records.reduce((counts, record) => {
    const key = record[field] || "UNKNOWN";
    counts[key] = (counts[key] || 0) + 1;
    return counts;
  }, {});
}

function renderStateList(id, counts, classMap = {}) {
  const root = document.getElementById(id);
  const entries = Object.entries(counts);

  if (entries.length === 0) {
    root.innerHTML = '<div class="empty">No data</div>';
    return;
  }

  root.innerHTML = entries
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([label, count]) => {
      const itemClass = classMap[label] || riskClass(label);
      return `
        <div class="state-row">
          <div class="state-left">
            <span class="state-dot ${itemClass}"></span>
            <span class="state-label">${label}</span>
          </div>
          <span class="state-value">${count}</span>
        </div>
      `;
    })
    .join("");
}

function renderTelemetryTable(events) {
  const root = document.getElementById("telemetryTable");
  const latestEvents = events.slice(0, 14);

  if (latestEvents.length === 0) {
    root.innerHTML = '<tr><td colspan="5">No telemetry events</td></tr>';
    return;
  }

  root.innerHTML = latestEvents
    .map(
      (event) => `
        <tr>
          <td title="${event.charger_id}">${event.charger_id}</td>
          <td><span class="status ${statusClass(event.status)}">${event.status}</span></td>
          <td>${decimalFormat.format(event.power_kw)} kW</td>
          <td title="${event.error_code || ""}">${event.error_code || "-"}</td>
          <td>${formatDate(event.heartbeat_at)}</td>
        </tr>
      `,
    )
    .join("");
}

function renderProblemList(summary) {
  const root = document.getElementById("problemList");
  const chargers = summary.top_problematic_chargers || [];

  if (chargers.length === 0) {
    root.innerHTML = '<div class="empty">No anomalies</div>';
    return;
  }

  root.innerHTML = chargers
    .map(
      (charger) => `
        <div class="compact-row">
          <span class="compact-title" title="${charger.charger_id}">${charger.charger_id}</span>
          <span class="compact-value">${charger.total_anomalies}</span>
        </div>
      `,
    )
    .join("");
}

function dayKey(value) {
  return new Date(value).toISOString().slice(0, 10);
}

function shortDayLabel(value) {
  return new Date(`${value}T00:00:00Z`).toLocaleDateString("en-GB", {
    day: "2-digit",
    month: "2-digit",
  });
}

function groupPowerByDay(events) {
  const grouped = events.reduce((days, event) => {
    const key = dayKey(event.heartbeat_at);
    if (!days[key]) {
      days[key] = { totalPower: 0, count: 0 };
    }
    days[key].totalPower += event.power_kw;
    days[key].count += 1;
    return days;
  }, {});

  return Object.entries(grouped)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([date, values]) => ({
      date,
      value: values.count === 0 ? 0 : values.totalPower / values.count,
    }));
}

function groupAnomaliesByTelemetryDay(anomalies, telemetryEvents) {
  const telemetryById = telemetryEvents.reduce((index, event) => {
    index[event.id] = event;
    return index;
  }, {});
  const grouped = anomalies.reduce((days, anomaly) => {
    const telemetry = telemetryById[anomaly.telemetry_event_id];
    const dateSource = telemetry ? telemetry.heartbeat_at : anomaly.detected_at;
    const key = dayKey(dateSource);
    days[key] = (days[key] || 0) + 1;
    return days;
  }, {});

  return Object.entries(grouped)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([date, value]) => ({ date, value }));
}

function fillMissingDays(series) {
  if (series.length === 0) {
    return [];
  }

  const valuesByDate = series.reduce((index, item) => {
    index[item.date] = item.value;
    return index;
  }, {});
  const start = new Date(`${series[0].date}T00:00:00Z`);
  const end = new Date(`${series[series.length - 1].date}T00:00:00Z`);
  const filled = [];

  for (
    const cursor = new Date(start);
    cursor <= end;
    cursor.setUTCDate(cursor.getUTCDate() + 1)
  ) {
    const date = cursor.toISOString().slice(0, 10);
    filled.push({ date, value: valuesByDate[date] || 0 });
  }

  return filled;
}

function renderBarTrend(id, series) {
  const root = document.getElementById(id);
  const data = fillMissingDays(series).slice(-10);

  if (data.length === 0) {
    root.innerHTML = '<div class="empty">No trend data</div>';
    return;
  }

  const width = 720;
  const height = 220;
  const padding = { top: 22, right: 18, bottom: 32, left: 34 };
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;
  const maxValue = Math.max(...data.map((item) => item.value), 1);
  const barGap = 8;
  const slotWidth = chartWidth / data.length;
  const barWidth = Math.max(8, slotWidth - barGap);

  const bars = data
    .map((item, index) => {
      const x = padding.left + index * slotWidth + (slotWidth - barWidth) / 2;
      const barHeight = (item.value / maxValue) * chartHeight;
      const y = padding.top + chartHeight - barHeight;
      return `
        <rect class="chart-bar" x="${x}" y="${y}" width="${barWidth}" height="${barHeight}" rx="3"></rect>
        <text class="chart-value" x="${x + barWidth / 2}" y="${y - 6}" text-anchor="middle">${Math.round(item.value)}</text>
        <text class="chart-label" x="${x + barWidth / 2}" y="${height - 10}" text-anchor="middle">${shortDayLabel(item.date)}</text>
      `;
    })
    .join("");

  root.innerHTML = `
    <svg class="chart" viewBox="0 0 ${width} ${height}" role="img" aria-label="Anomalies over time">
      <line class="chart-axis" x1="${padding.left}" y1="${padding.top + chartHeight}" x2="${width - padding.right}" y2="${padding.top + chartHeight}"></line>
      <line class="chart-axis" x1="${padding.left}" y1="${padding.top}" x2="${padding.left}" y2="${padding.top + chartHeight}"></line>
      <line class="chart-grid" x1="${padding.left}" y1="${padding.top}" x2="${width - padding.right}" y2="${padding.top}"></line>
      ${bars}
    </svg>
  `;
}

function renderLineTrend(id, series) {
  const root = document.getElementById(id);
  const data = fillMissingDays(series).slice(-10);

  if (data.length === 0) {
    root.innerHTML = '<div class="empty">No trend data</div>';
    return;
  }

  const width = 520;
  const height = 220;
  const padding = { top: 22, right: 18, bottom: 32, left: 34 };
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;
  const maxValue = Math.max(...data.map((item) => item.value), 1);
  const step = data.length > 1 ? chartWidth / (data.length - 1) : chartWidth;

  const points = data.map((item, index) => {
    const x = padding.left + index * step;
    const y = padding.top + chartHeight - (item.value / maxValue) * chartHeight;
    return { ...item, x, y };
  });
  const path = points
    .map((point, index) => `${index === 0 ? "M" : "L"} ${point.x} ${point.y}`)
    .join(" ");
  const areaPath = `${path} L ${points[points.length - 1].x} ${padding.top + chartHeight} L ${points[0].x} ${padding.top + chartHeight} Z`;

  const labels = points
    .map(
      (point, index) => `
        <circle cx="${point.x}" cy="${point.y}" r="4" fill="var(--blue)"></circle>
        ${
          index % 2 === 0 || index === points.length - 1
            ? `<text class="chart-label" x="${point.x}" y="${height - 10}" text-anchor="middle">${shortDayLabel(point.date)}</text>`
            : ""
        }
      `,
    )
    .join("");

  root.innerHTML = `
    <svg class="chart" viewBox="0 0 ${width} ${height}" role="img" aria-label="Average power over time">
      <line class="chart-axis" x1="${padding.left}" y1="${padding.top + chartHeight}" x2="${width - padding.right}" y2="${padding.top + chartHeight}"></line>
      <line class="chart-axis" x1="${padding.left}" y1="${padding.top}" x2="${padding.left}" y2="${padding.top + chartHeight}"></line>
      <line class="chart-grid" x1="${padding.left}" y1="${padding.top}" x2="${width - padding.right}" y2="${padding.top}"></line>
      <path class="chart-area" d="${areaPath}"></path>
      <path class="chart-line" d="${path}"></path>
      ${labels}
      <text class="chart-value" x="${width - padding.right}" y="${padding.top - 6}" text-anchor="end">${decimalFormat.format(maxValue)} kW max</text>
    </svg>
  `;
}

function renderAnomalyList(anomalies) {
  const root = document.getElementById("anomalyList");
  const latestAnomalies = anomalies.slice(0, 7);

  if (latestAnomalies.length === 0) {
    root.innerHTML = '<div class="empty">No anomalies</div>';
    return;
  }

  root.innerHTML = latestAnomalies
    .map(
      (anomaly) => `
        <div class="compact-row">
          <span class="compact-title" title="${anomaly.charger_id}">${anomaly.charger_id}</span>
          <span class="status ${riskClass(anomaly.severity)}">${anomaly.severity}</span>
        </div>
      `,
    )
    .join("");
}

async function loadDashboard() {
  refreshButton.disabled = true;

  try {
    const [health, summary, anomalyRate, biRecords, telemetry, anomalies] =
      await Promise.all([
        fetchJson("/api/health"),
        fetchJson("/api/insights/summary"),
        fetchJson("/api/insights/anomaly-rate"),
        fetchJson("/api/bi/operational-insights"),
        fetchJson("/api/telemetry"),
        fetchJson("/api/anomalies"),
      ]);

    apiStatus.textContent = health.status === "ok" ? "API online" : "API degraded";
    apiStatus.classList.toggle("error", health.status !== "ok");
    lastUpdated.textContent = `Updated ${new Date().toLocaleTimeString("en-GB", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    })}`;

    renderKpis(summary);
    renderBarTrend("anomalyTrend", groupAnomaliesByTelemetryDay(anomalies, telemetry));
    renderLineTrend("powerTrend", groupPowerByDay(telemetry));
    renderRiskChart(biRecords);
    renderStateList("healthChart", countBy(biRecords, "health_state"), {
      HEALTHY: "low",
      WARNING: "medium",
      CRITICAL: "high",
    });
    renderStateList("severityChart", anomalyRate.severity_distribution, {
      HIGH: "high",
      MEDIUM: "medium",
    });
    renderTelemetryTable(telemetry);
    renderProblemList(summary);
    renderAnomalyList(anomalies);
  } catch (error) {
    apiStatus.textContent = "API error";
    apiStatus.classList.add("error");
    lastUpdated.textContent = error.message;
  } finally {
    refreshButton.disabled = false;
  }
}

refreshButton.addEventListener("click", loadDashboard);
loadDashboard();
setInterval(loadDashboard, 15000);
