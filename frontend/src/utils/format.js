export function formatTime(isoValue) {
  if (!isoValue) {
    return "—";
  }
  return new Date(isoValue).toLocaleTimeString("en-IN", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: true,
    timeZone: "Asia/Kolkata",
  });
}

export function formatDateTime(isoValue) {
  if (!isoValue) {
    return "—";
  }
  const formatted = new Date(isoValue).toLocaleString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    hour12: true,
    timeZone: "Asia/Kolkata",
  });
  return `${formatted} IST`;
}

export function formatNumber(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return "—";
  }
  return Number(value).toLocaleString("en-IN");
}
