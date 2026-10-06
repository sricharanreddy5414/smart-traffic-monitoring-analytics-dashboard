import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { STATUS_COLORS, congestionDistribution } from "../utils/chartData";

export default function CongestionChart({ locations }) {
  const bars = (locations || []).map((location) => ({
    location: location.location_name,
    congestion: location.congestion_percentage,
    status: location.congestion_status,
  }));
  const distribution = congestionDistribution(locations);
  const pieData = distribution.filter((item) => item.value > 0);

  return (
    <section className="panel">
      <div className="panel-heading">
        <h2>Congestion Level</h2>
        <p>Calculated based on current vehicle count compared with estimated road capacity.</p>
      </div>
      {bars.length === 0 ? (
        <p className="empty-copy">No traffic data available.</p>
      ) : (
        <div className="split-charts">
          <div className="chart-box">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={bars} layout="vertical" margin={{ top: 8, right: 16, left: 24, bottom: 0 }}>
                <CartesianGrid stroke="#e2e8ee" strokeDasharray="3 3" />
                <XAxis type="number" unit="%" tick={{ fontSize: 12 }} />
                <YAxis type="category" dataKey="location" width={110} tick={{ fontSize: 12 }} />
                <Tooltip />
                <Bar dataKey="congestion" name="Congestion %" radius={[0, 4, 4, 0]}>
                  {bars.map((item) => (
                    <Cell key={item.location} fill={STATUS_COLORS[item.status] || "#0b3a5b"} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="distribution">
            <h3>Congestion Distribution</h3>
            <div className="chart-box chart-box-short">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={pieData} dataKey="value" nameKey="name" innerRadius={48} outerRadius={78} paddingAngle={2}>
                    {pieData.map((item) => (
                      <Cell key={item.name} fill={item.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <ul className="distribution-list">
              {distribution.map((item) => (
                <li key={item.name}>
                  <span className="swatch" style={{ background: item.color }} />
                  {item.name}: {item.value}
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </section>
  );
}
