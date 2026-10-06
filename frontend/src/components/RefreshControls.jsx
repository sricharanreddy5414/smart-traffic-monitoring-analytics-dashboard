export default function RefreshControls({
  onRefresh,
  onSimulate,
  autoRefresh,
  onToggleAuto,
  busy,
}) {
  return (
    <section className="controls">
      <div className="control-buttons">
        <button type="button" className="btn btn-secondary" onClick={onRefresh} disabled={Boolean(busy)}>
          {busy === "refresh" ? "Refreshing..." : "Refresh Data"}
        </button>
        <button type="button" className="btn btn-primary" onClick={onSimulate} disabled={Boolean(busy)}>
          {busy === "simulate" ? "Updating traffic..." : "Simulate Traffic Update"}
        </button>
      </div>
      <label className="auto-toggle">
        <input type="checkbox" checked={autoRefresh} onChange={onToggleAuto} />
        Automatic refresh every 10 seconds
      </label>
    </section>
  );
}
