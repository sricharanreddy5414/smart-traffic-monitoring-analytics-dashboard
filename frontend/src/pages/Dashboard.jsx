import { useCallback, useEffect, useRef, useState } from "react";
import CongestionChart from "../components/CongestionChart";
import ErrorState from "../components/ErrorState";
import Header from "../components/Header";
import LoadingState from "../components/LoadingState";
import PredictionCard from "../components/PredictionCard";
import RefreshControls from "../components/RefreshControls";
import SpeedChart from "../components/SpeedChart";
import SummaryCard from "../components/SummaryCard";
import TrafficLocationMap from "../components/TrafficLocationMap";
import TrafficOverviewChart from "../components/TrafficOverviewChart";
import TrafficTable from "../components/TrafficTable";
import { getAnalytics, getPrediction, getTraffic, simulateTraffic } from "../services/api";
import { formatNumber } from "../utils/format";

export default function Dashboard() {
  const [traffic, setTraffic] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [busy, setBusy] = useState("");
  const requestId = useRef(0);

  const load = useCallback(async () => {
    const currentRequest = requestId.current + 1;
    requestId.current = currentRequest;
    const [trafficData, analyticsData, predictionData] = await Promise.all([
      getTraffic(),
      getAnalytics(),
      getPrediction(),
    ]);
    if (currentRequest !== requestId.current) {
      return;
    }
    setTraffic(trafficData);
    setAnalytics(analyticsData);
    setPrediction(predictionData);
    setError("");
  }, []);

  useEffect(() => {
    let active = true;
    setLoading(true);
    load()
      .catch(() => {
        if (active) {
          setError("Unable to retrieve traffic data.");
        }
      })
      .finally(() => {
        if (active) {
          setLoading(false);
        }
      });
    return () => {
      active = false;
    };
  }, [load]);

  useEffect(() => {
    if (!autoRefresh || loading) {
      return undefined;
    }
    const timer = setInterval(() => {
      load().catch(() => setError("Unable to retrieve traffic data."));
    }, 10000);
    return () => clearInterval(timer);
  }, [autoRefresh, load, loading]);

  async function handleRefresh() {
    setBusy("refresh");
    try {
      await load();
    } catch {
      setError("Unable to retrieve traffic data.");
    } finally {
      setBusy("");
    }
  }

  async function handleSimulate() {
    setBusy("simulate");
    try {
      await simulateTraffic();
      await load();
    } catch {
      setError("Unable to retrieve traffic data.");
    } finally {
      setBusy("");
    }
  }

  const locations = traffic?.locations || [];
  const hasData = locations.length > 0;

  return (
    <div className="page">
      <Header
        lastUpdated={traffic?.last_updated}
        storageMode={traffic?.storage_mode}
        liveOn={autoRefresh}
      />
      <main>
        <RefreshControls
          onRefresh={handleRefresh}
          onSimulate={handleSimulate}
          autoRefresh={autoRefresh}
          onToggleAuto={() => setAutoRefresh((current) => !current)}
          busy={busy}
        />

        {loading ? <LoadingState /> : null}
        {!loading && error && !hasData ? <ErrorState onRetry={handleRefresh} /> : null}
        {!loading && error && hasData ? (
          <p className="error-banner" role="alert">
            Unable to retrieve traffic data.
          </p>
        ) : null}
        {!loading && !error && !hasData ? <p className="empty-copy panel">No traffic data available.</p> : null}

        {!loading && hasData ? (
          <>
            <section className="summary-grid">
              <SummaryCard label="Total Monitored Locations" value={formatNumber(analytics?.total_locations)} />
              <SummaryCard label="Total Vehicles" value={formatNumber(analytics?.total_vehicles)} />
              <SummaryCard
                label="Average Speed"
                value={`${formatNumber(analytics?.average_speed)} km/h`}
              />
              <SummaryCard
                label="Congested Locations"
                value={formatNumber(analytics?.congested_locations)}
                detail="HIGH or CRITICAL"
              />
              <SummaryCard
                label="Average Congestion"
                value={`${formatNumber(analytics?.average_congestion)}%`}
              />
            </section>

            <section className="insight">
              <p>
                Busiest location: <strong>{analytics?.busiest_location || "—"}</strong>
              </p>
              <p>
                Least busy location: <strong>{analytics?.least_busy_location || "—"}</strong>
              </p>
              <p>
                Highest congestion: <strong>{analytics?.highest_congestion_location || "—"}</strong>
              </p>
              <p>
                Lowest congestion: <strong>{analytics?.lowest_congestion_location || "—"}</strong>
              </p>
            </section>

            <div className="two-col">
              <TrafficOverviewChart history={traffic.history} locations={locations} />
              <SpeedChart locations={locations} />
            </div>
            <CongestionChart locations={locations} />
            <PredictionCard prediction={prediction} />
            <TrafficLocationMap locations={locations} />
            <TrafficTable locations={locations} />
          </>
        ) : null}

        <footer className="footer">
          <p>
            {traffic?.disclaimer ||
              "Traffic data is simulated for academic demonstration. The architecture can later be connected to IoT sensors, CCTV/computer vision systems, GPS feeds, or external traffic APIs."}
          </p>
          <p>Congestion bands: LOW 0–40, MEDIUM 41–65, HIGH 66–85, CRITICAL 86+.</p>
        </footer>
      </main>
    </div>
  );
}
