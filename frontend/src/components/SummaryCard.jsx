export default function SummaryCard({ label, value, detail }) {
  return (
    <article className="summary-card">
      <p className="summary-label">{label}</p>
      <p className="summary-value">{value}</p>
      {detail ? <p className="summary-detail">{detail}</p> : null}
    </article>
  );
}
