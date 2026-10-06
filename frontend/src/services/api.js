const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:7071/api";

async function request(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  if (options.body) {
    headers["Content-Type"] = "application/json";
  }

  let response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, { ...options, headers });
  } catch (error) {
    const failure = new Error("Unable to retrieve traffic data.");
    failure.cause = error;
    throw failure;
  }

  let payload = null;
  try {
    payload = await response.json();
  } catch (error) {
    payload = null;
  }

  if (!response.ok) {
    const failure = new Error(payload?.error || "Unable to retrieve traffic data.");
    failure.status = response.status;
    throw failure;
  }

  return payload;
}

export function getTraffic() {
  return request("/traffic");
}

export function getLocation(locationId) {
  return request(`/traffic/${encodeURIComponent(locationId)}`);
}

export function getAnalytics() {
  return request("/traffic/analytics");
}

export function getPrediction(locationId) {
  const query = locationId ? `?location_id=${encodeURIComponent(locationId)}` : "";
  return request(`/traffic/prediction${query}`);
}

export function simulateTraffic() {
  return request("/traffic/simulate", {
    method: "POST",
    body: JSON.stringify({}),
  });
}

export { API_BASE_URL };
