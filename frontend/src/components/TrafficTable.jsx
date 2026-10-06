import { formatDateTime, formatNumber } from "../utils/format";
import { statusClass } from "../utils/chartData";

export default function TrafficTable({ locations }) {
  if (!locations || locations.length === 0) {
    return (
      <section className="panel">
        <div className="panel-heading">
          <h2>Traffic Table</h2>
        </div>
        <p className="empty-copy">No traffic data available.</p>
      </section>
    );
  }

  return (
    <section className="panel">
      <div className="panel-heading">
        <h2>Traffic Table</h2>
        <p>Latest reading for each location. Congestion % = (vehicles / road capacity) × 100.</p>
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Location</th>
              <th>Vehicles</th>
              <th>Average Speed</th>
              <th>Road Capacity</th>
              <th>Congestion %</th>
              <th>Status</th>
              <th>Last Updated</th>
            </tr>
          </thead>
          <tbody>
            {locations.map((location) => (
              <tr key={location.location_id}>
                <td>{location.location_name}</td>
                <td>{formatNumber(location.vehicle_count)}</td>
                <td>{formatNumber(location.average_speed)} km/h</td>
                <td>{formatNumber(location.road_capacity)}</td>
                <td>{location.congestion_percentage}%</td>
                <td>
                  <span className={statusClass(location.congestion_status)}>{location.congestion_status}</span>
                </td>
                <td>{formatDateTime(location.timestamp)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
