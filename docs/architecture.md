# Architecture

Smart Traffic Monitoring and Analytics Dashboard is a small cloud application. A browser shows traffic for six Bengaluru locations. Azure Functions calculates congestion, analytics, and a short-term prediction. Azure Cosmos DB stores the readings when it is configured.

Traffic data is simulated for academic demonstration. The architecture can later be connected to IoT sensors, CCTV/computer vision systems, GPS feeds, or external traffic APIs.

## System architecture

```
User
  |
  v
React Dashboard
  |
  v
Azure Static Web Apps
  |
  v
Azure Functions
  |
  v
Azure Cosmos DB
  |
  v
Traffic Data
  |
  v
Analytics Engine
  |
  +----> Congestion Calculation
  |
  +----> Traffic Trends
  |
  +----> Short-Term Prediction
  |
  v
Dashboard Visualization
```

Locally, the same Functions API runs with `func start`. If Cosmos DB credentials are empty, the API writes to `backend/.local_data/traffic_store.json`. That file is created from `data/sample_traffic_data.json`. It is a local development store, not a fake success response from Cosmos DB.

## Components

| Component | Responsibility |
| --- | --- |
| React dashboard | Calls the API and draws cards, charts, the table, the map, and the prediction |
| Azure Static Web Apps | Hosts the built React files |
| Azure Functions | HTTP API in Python |
| Azure Cosmos DB | Stores one document per traffic reading |
| Analytics modules | Congestion, summaries, moving average, and simulation |
| GitHub Actions | Runs tests and can deploy after secrets are configured |

The backend is one Function App, not a set of microservices. The frontend is one React page.

## Data flow

1. The dashboard requests `/api/traffic`, `/api/traffic/analytics`, and `/api/traffic/prediction`.
2. The repository reads every stored reading.
3. Congestion is calculated while building the response. It is not saved as a separate field.
4. The dashboard draws the latest reading for each location and uses history for the line chart.
5. Simulate Traffic Update creates six new readings, saves them, and the dashboard requests the data again.

## Frontend flow

`frontend/src/pages/Dashboard.jsx` loads the three API responses together. Summary cards use the analytics response. Charts and the table use the traffic response. The prediction section uses the prediction response. Refresh Data repeats the load. The auto-refresh checkbox polls every 10 seconds. It does not invent new traffic values. Only Simulate Traffic Update writes new readings.

The API address comes from `VITE_API_BASE_URL`.

## Backend flow

`function_app.py` defines the HTTP routes and returns JSON. `handlers.py` contains the API behaviour so it can be tested without the Functions host. `repository.py` chooses Cosmos DB or the local JSON file.

Routes:

- `GET /api/traffic`
- `GET /api/traffic/{location_id}`
- `GET /api/traffic/analytics`
- `GET /api/traffic/prediction`
- `POST /api/traffic/simulate`
- `GET /api/health`

## Database flow

Cosmos DB account, suggested name `cosmos-smart-traffic-<unique>`.

- Database: `TrafficDB`
- Container: `TrafficData`
- Partition key: `/location_id`

Each item is one reading. The partition key matches the field used to fetch a single location. On first use, if the container has no items, the API inserts the sample file. If the container already has items, it does not overwrite them.

Required settings are `COSMOS_ENDPOINT`, `COSMOS_KEY`, `COSMOS_DATABASE`, and `COSMOS_CONTAINER`. The key stays in environment variables.

## Analytics flow

`analytics.py` keeps the newest reading for each location. From those six readings it calculates totals, averages, congested locations, and the busiest and quietest locations. A location is congested when congestion is above 65 percent, which is HIGH or CRITICAL.

## Prediction flow

`prediction.py` sorts readings for one location by time, takes up to five recent vehicle counts, and returns their average rounded to the nearest integer. The response label is `Moving Average`.

Worked example: 400, 430, 450, 470, and 460. The sum is 2210. The average is 442.

## Congestion flow

```
congestion_percentage = (vehicle_count / road_capacity) * 100
```

| Percentage | Status |
| --- | --- |
| 0–40 | LOW |
| 41–65 | MEDIUM |
| 66–85 | HIGH |
| 86 or more | CRITICAL |

Example: 450 vehicles and a capacity of 600 gives 75 percent, so the status is HIGH.

## Azure services

| Service | Role in this project |
| --- | --- |
| Resource group | Holds the project resources so they can be deleted together |
| Cosmos DB | Document store for traffic readings |
| Functions | Serverless HTTP API |
| Static Web Apps | Hosts the React build |
| GitHub | Source control |
| GitHub Actions | Build, test, and optional deploy |

No Kubernetes cluster, message bus, or separate machine learning service is used.
