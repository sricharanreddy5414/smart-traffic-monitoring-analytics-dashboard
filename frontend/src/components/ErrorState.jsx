export default function ErrorState({ onRetry }) {
  return (
    <div className="state-box state-error" role="alert">
      <p>Unable to retrieve traffic data.</p>
      {onRetry ? (
        <button type="button" className="btn btn-primary" onClick={onRetry}>
          Try again
        </button>
      ) : null}
    </div>
  );
}
