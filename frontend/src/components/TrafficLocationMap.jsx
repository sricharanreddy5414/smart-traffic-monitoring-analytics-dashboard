import { mapPosition, statusClass } from "../utils/chartData";

export default function TrafficLocationMap({ locations }) {
  return (
    <section className="panel">
      <div className="panel-heading">
        <h2>Traffic Map</h2>
        <p>Schematic location view of Bengaluru. Green is LOW, yellow is MEDIUM, orange is HIGH, and red is CRITICAL.</p>
      </div>
      {!locations || locations.length === 0 ? (
        <p className="empty-copy">No traffic data available.</p>
      ) : (
        <div className="city-map" aria-label="Schematic map of monitored Bengaluru locations">
          <span className="north">N</span>
          <span className="city-name">Bengaluru</span>
          {locations.map((location) => (
            <div
              key={location.location_id}
              className={`pin pin-${String(location.congestion_status).toLowerCase()}`}
              style={mapPosition(location)}
            >
              <span className="pin-dot" />
              <span className="pin-card">
                <strong>{location.location_name}</strong>
                <span className={statusClass(location.congestion_status)}>{location.congestion_status}</span>
              </span>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
