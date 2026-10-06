import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { buildTrendRows, seriesFor } from "../utils/chartData";

export default function TrafficOverviewChart({ history, locations }) {
  const data = buildTrendRows(history);
  const series = seriesFor(locations);

  return (
    <section className="panel">
      <div className="panel-heading">
        <h2>Traffic Overview</h2>
        <p>Vehicle count over time for each monitored location.</p>
      </div>
      {data.length === 0 ? (
        <p className="empty-copy">No traffic data available.</p>
      ) : (
        <div className="chart-box">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 8, right: 12, left: 0, bottom: 0 }}>
              <CartesianGrid stroke="#e2e8ee" strokeDasharray="3 3" />
              <XAxis dataKey="time" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Legend />
              {series.map((item) => (
                <Line
                  key={item.name}
                  type="monotone"
                  dataKey={item.name}
                  stroke={item.color}
                  strokeWidth={2}
                  dot={false}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </section>
  );
}
