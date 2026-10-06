import { formatTime } from "./format";

export const STATUS_COLORS = {
  LOW: "#1f7a4d",
  MEDIUM: "#9a7b00",
  HIGH: "#d46a00",
  CRITICAL: "#c0392b",
};

const SERIES_COLORS = ["#0b3a5b", "#c0392b", "#d46a00", "#1f7a4d", "#146c94", "#5c4d7a"];

export function statusClass(status) {
  return `status status-${String(status || "").toLowerCase()}`;
}

export function buildTrendRows(history) {
  const rows = new Map();
  (history || []).forEach((record) => {
    if (!rows.has(record.timestamp)) {
      rows.set(record.timestamp, {
        timestamp: record.timestamp,
        time: formatTime(record.timestamp),
      });
    }
    rows.get(record.timestamp)[record.location_name] = record.vehicle_count;
  });
  return Array.from(rows.values()).sort((left, right) => left.timestamp.localeCompare(right.timestamp));
}

export function seriesFor(locations) {
  return (locations || []).map((location, index) => ({
    name: location.location_name,
    color: SERIES_COLORS[index % SERIES_COLORS.length],
  }));
}

export function congestionDistribution(locations) {
  return ["LOW", "MEDIUM", "HIGH", "CRITICAL"].map((status) => ({
    name: status,
    value: (locations || []).filter((location) => location.congestion_status === status).length,
    color: STATUS_COLORS[status],
  }));
}

export function mapPosition(location) {
  const minLat = 12.8;
  const maxLat = 13.08;
  const minLng = 77.55;
  const maxLng = 77.78;
  const x = 12 + ((location.longitude - minLng) / (maxLng - minLng)) * 74;
  const y = 14 + ((maxLat - location.latitude) / (maxLat - minLat)) * 68;
  return { left: `${x}%`, top: `${y}%` };
}
