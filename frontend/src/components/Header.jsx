import { formatDateTime } from "../utils/format";

export default function Header({ lastUpdated, storageMode, liveOn }) {
  const storeLabel = storageMode === "cosmos-db" ? "Azure Cosmos DB" : "Local JSON store";

  return (
    <header className="header">
      <div>
        <p className="eyebrow">College mini project · SIH Smart Transportation</p>
        <h1>Smart Traffic Monitoring and Analytics Dashboard</h1>
        <p className="subtitle">Cloud-Based Traffic Monitoring and Analytics</p>
      </div>
      <div className="badge-row">
        <span className="badge">Azure Cloud</span>
        <span className={`badge ${liveOn ? "badge-live" : ""}`}>
          {liveOn ? "LIVE MONITORING: ON" : "LIVE MONITORING: OFF"}
        </span>
        <span className="badge">Last updated: {formatDateTime(lastUpdated)}</span>
      </div>
      <p className="header-note">
        Data store: {storeLabel}. Traffic data is simulated for academic demonstration.
      </p>
    </header>
  );
}
