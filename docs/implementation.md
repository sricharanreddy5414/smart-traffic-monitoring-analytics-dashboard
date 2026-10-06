# Implementation

This note explains how the college project is built. The goal is that you can describe every part in a viva.

## 1. Project initialization

The repository is `smart-traffic-monitoring-analytics-dashboard`. The frontend is a Vite React app. The backend is one Python Azure Functions app. Sample readings live in `data/sample_traffic_data.json`. Documentation lives in `docs/`.

Git ignores `node_modules`, `.env`, `local.settings.json`, Python cache folders, and the local traffic file created at runtime.

## 2. Frontend implementation

The page is `frontend/src/pages/Dashboard.jsx`. Reusable pieces are in `frontend/src/components/`:

- Header
- SummaryCard
- TrafficOverviewChart
- SpeedChart
- CongestionChart
- TrafficTable
- TrafficLocationMap
- PredictionCard
- LoadingState
- ErrorState
- RefreshControls

`frontend/src/services/api.js` is the only place that builds API URLs. Charts use Recharts. The map is a schematic view based on latitude and longitude. It is not Google Maps.

## 3. Backend implementation

`function_app.py` registers the HTTP functions. `handlers.py` prepares JSON and status codes. Calculation code is split into small modules:

- `congestion.py`
- `analytics.py`
- `prediction.py`
- `simulation.py`
- `validation.py`
- `locations.py`
- `repository.py`

This keeps the Azure decorator file short and lets unit tests call the same logic the API uses.

## 4. Database implementation

`repository.py` checks the environment.

- When `COSMOS_ENDPOINT` and `COSMOS_KEY` are set, it uses Azure Cosmos DB.
- When both are empty, it uses a JSON file under `backend/.local_data/`.
- When only one of them is set, the API returns an error instead of pretending Cosmos DB is connected.

The Cosmos container is `TrafficData` in database `TrafficDB`, partitioned by `/location_id`. System fields such as `_etag` are removed before a response is sent.

## 5. Traffic data model

Each reading contains:

- `id`
- `location_id`
- `location_name`
- `timestamp`
- `vehicle_count`
- `average_speed`
- `road_capacity`
- `latitude`
- `longitude`

The API adds `congestion_percentage` and `congestion_status` when it responds. Those two values are calculated, not typed in by hand.

## 6. Traffic data generation

`backend/generate_sample_data.py` builds 13 half-hour readings for each of the six locations on 6 October 2026. The latest point is chosen so the demo includes LOW, MEDIUM, HIGH, and CRITICAL. The file header states that the data is simulated.

Regenerate it with:

```powershell
cd backend
python generate_sample_data.py
```

## 7. API implementation

The Functions host adds the `/api` prefix. Each handler returns JSON and an HTTP status code. Unknown locations return 404. Invalid JSON sent to the simulate endpoint returns 400. A Cosmos DB connection failure returns 503. An unexpected failure returns 500 with `Unable to retrieve traffic data.`

## 8. Congestion calculation

```
congestion_percentage = (vehicle_count / road_capacity) * 100
```

450 / 600 = 0.75, which is 75 percent, which is HIGH. The bands are 0–40 LOW, 41–65 MEDIUM, 66–85 HIGH, and 86+ CRITICAL.

## 9. Analytics

Analytics uses only the latest reading at each location. Total vehicles is the sum of those vehicle counts. Average speed and average congestion are means of the six locations. Congested locations are the ones above 65 percent. Busiest means the highest vehicle count. Highest congestion means the highest percentage. Those can be different locations if a smaller road is fuller than a larger road.

## 10. Prediction

For each location the code takes the most recent vehicle counts, up to five, and averages them. The result is rounded to a whole number. The dashboard labels this Moving Average. It is not a trained model.

## 11. Dashboard integration

On load, the page waits for traffic, analytics, and prediction. The first visit shows `Loading traffic data...`. If the API cannot be reached, it shows `Unable to retrieve traffic data.` and does not crash. If the API returns no locations, it shows `No traffic data available.`

Simulate Traffic Update posts to `/api/traffic/simulate`, then loads the three endpoints again. Refresh Data only reloads. The 10-second timer also only reloads.

## 12. Azure deployment

The API is deployed as the Python 3.11 Function App `func-smart-traffic-dashboard` in resource group `rg-smart-traffic-dashboard` (Central India). It reads and writes Cosmos DB account `cosmos-smart-traffic`, database `TrafficDB`, container `TrafficData`, partition key `/location_id`. The public API root is `https://func-smart-traffic-dashboard.azurewebsites.net/api`. Health checks report `storage_mode` `cosmos-db` and `data_source` `simulated`.

The React dashboard is built with `VITE_API_BASE_URL` set to that API root. It is hosted as an Azure Storage static website on `stsmarttrafficweb5414`. The public URL is `https://stsmarttrafficweb5414.z29.web.core.windows.net/`. Index and error documents are both `index.html`.

Azure Static Web Apps could not be deployed because the Azure for Students subscription restricts resource creation to regions that are not supported by Azure Static Web Apps. Therefore, Azure Storage Static Website hosting is used for the React frontend. The Function App storage account `stsmarttraffic5414` is separate and is not the public website. The readings remain simulated academic data.

Step-by-step notes and the region limit are in `docs/azure-deployment.md`.

## 13. GitHub Actions

`.github/workflows/azure-deploy.yml` runs the Python unit tests and `npm run build` on every push and pull request. Deployment jobs run only on a push to `main` when the repository variable `DEPLOY_TO_AZURE` is `true`. The frontend job uploads the Vite build to the `$web` container of `stsmarttrafficweb5414`. The backend job publishes the Function App. Secrets are read from GitHub settings. They are not written in the workflow file.
