import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export default function SpeedChart({ locations }) {
  const data = (locations || []).map((location) => ({
    location: location.location_name,
    speed: location.average_speed,
  }));

  return (
    <section className="panel">
      <div className="panel-heading">
        <h2>Average Speed</h2>
        <p>Latest average speed at each location, in km/h.</p>
      </div>
      {data.length === 0 ? (
        <p className="empty-copy">No traffic data available.</p>
      ) : (
        <div className="chart-box">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} margin={{ top: 8, right: 12, left: 0, bottom: 8 }}>
              <CartesianGrid stroke="#e2e8ee" strokeDasharray="3 3" />
              <XAxis dataKey="location" tick={{ fontSize: 11 }} interval={0} angle={-18} height={60} textAnchor="end" />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Bar dataKey="speed" name="Average speed (km/h)" fill="#146c94" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </section>
  );
}
