import { formatNumber } from "../utils/format";

export default function PredictionCard({ prediction }) {
  const rows = prediction?.predictions || (prediction?.location ? [prediction] : []);

  return (
    <section className="panel">
      <div className="panel-heading">
        <h2>Short-Term Traffic Prediction</h2>
        <p>Short-term prediction using a moving average of recent traffic observations.</p>
      </div>
      <p className="method-line">
        Prediction Method: <strong>Moving Average</strong>
      </p>
      {rows.length === 0 ? (
        <p className="empty-copy">No traffic data available.</p>
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Location</th>
                <th>Current Vehicles</th>
                <th>Predicted Vehicles</th>
                <th>Recent Counts</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.location_id || row.location}>
                  <td>{row.location}</td>
                  <td>{formatNumber(row.current_vehicle_count)}</td>
                  <td>{formatNumber(row.predicted_vehicle_count)}</td>
                  <td>{(row.recent_vehicle_counts || []).join(", ")}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
