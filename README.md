# Smart Traffic Monitoring and Analytics Dashboard

Cloud-based college mini project for monitoring simulated traffic at six Bengaluru locations, calculating congestion, and showing a short-term prediction.

Traffic data in this academic prototype is simulated. The system is designed so that real traffic sensors, CCTV systems, GPS feeds, or external traffic APIs can be integrated in future versions.

## Project description

The dashboard collects traffic readings, stores them, and turns them into analytics a viewer can understand in a few minutes. Each reading has a location, time, vehicle count, average speed, and road capacity. The backend calculates congestion from those numbers. It does not use a hardcoded congestion label.

This is a course mini project. It is not a commercial product.

## Problem statement

Urban traffic congestion increases due to inefficient monitoring and lack of predictive analytics. This project is a cloud-hosted traffic monitoring system that collects traffic data, performs analytics, and visualizes congestion patterns using scalable cloud infrastructure.

## Objectives

- Monitor six Bengaluru locations with a clear traffic data model.
- Store readings in Azure Cosmos DB when Azure is configured.
- Expose the data through Azure Functions HTTP APIs.
- Calculate congestion, summary analytics, and a moving-average prediction.
- Show the results on a React dashboard.
- Simulate a new reading during a viva or project evaluation.
- Deploy the frontend with an Azure Storage static website and the backend with Azure Functions.
- Keep the source in GitHub and build it with GitHub Actions.

## Features

- Summary cards for locations, vehicles, speed, congested locations, and average congestion.
- Vehicle-count trend chart and average-speed chart.
- Congestion level chart and congestion distribution.
- Traffic table with status badges: LOW, MEDIUM, HIGH, CRITICAL.
- Schematic Bengaluru location view.
- Short-term prediction using a moving average.
- Refresh Data and Simulate Traffic Update buttons.
- Optional automatic refresh every 10 seconds.
- Loading, empty, and error states.
- Local JSON storage when Cosmos DB credentials are not configured yet.

## Technology stack

| Layer | Technology |
| --- | --- |
| Frontend | React, Vite, JavaScript, HTML, CSS, Recharts |
| Backend | Python, Azure Functions |
| Database | Azure Cosmos DB |
| Frontend hosting | Azure Storage static website |
| Source control | GitHub |
| CI/CD | GitHub Actions |

## System architecture

```
User
  |
  v
Azure Storage Static Website
  |
  v
React/Vite Dashboard
  |
  v
Azure Functions
  |
  v
Azure Cosmos DB
  |
  +--> Traffic Data
  |
  +--> Analytics
  |
  +--> Congestion Calculation
  |
  +--> Short-Term Prediction
  |
  v
Dashboard
```

Azure Static Web Apps could not be deployed because the Azure for Students subscription restricts resource creation to regions that are not supported by Azure Static Web Apps. Therefore, Azure Storage Static Website hosting is used for the React frontend.

For local development, the React app calls `http://localhost:7071/api`. If Cosmos DB settings are empty, Azure Functions stores readings in a local JSON file instead. See [docs/architecture.md](docs/architecture.md).

## How it works

1. Sample readings for MG Road, Silk Board, Electronic City, Whitefield, Marathahalli, and Hebbal are loaded.
2. The API returns the latest reading for each location and the history used by the charts.
3. Congestion percentage is `(vehicle_count / road_capacity) * 100`.
4. Analytics summarize the latest readings.
5. Prediction averages the recent vehicle counts at each location.
6. Simulate Traffic Update appends one new realistic reading per location and the dashboard reloads.

## Traffic analytics

`GET /api/traffic/analytics` calculates:

- total locations
- total vehicles
- average speed
- average congestion
- number of congested locations (HIGH or CRITICAL, above 65%)
- busiest and least busy locations
- highest and lowest congestion locations

## Predictive analytics

The prediction is a moving average of the latest observations, usually five readings. It is a basic academic method, not a machine learning model.

Example: vehicle counts 400, 430, 450, 470, and 460 average to 442. The API returns 442 as the predicted vehicle count.

## Azure services

These resources are deployed in the Azure for Students subscription, in Central India. Details and the Static Web Apps limit are in [docs/azure-deployment.md](docs/azure-deployment.md).

| Resource | Name |
| --- | --- |
| Resource group | `rg-smart-traffic-dashboard` |
| Cosmos DB account | `cosmos-smart-traffic` |
| Database | `TrafficDB` |
| Container | `TrafficData` |
| Partition key | `/location_id` |
| Function App | `func-smart-traffic-dashboard` |
| API | `https://func-smart-traffic-dashboard.azurewebsites.net/api` |
| Frontend storage account | `stsmarttrafficweb5414` |
| Public website | `https://stsmarttrafficweb5414.z29.web.core.windows.net/` |
| Function App storage | `stsmarttraffic5414` |

`stsmarttraffic5414` exists because the Function App host requires it. The public website uses the separate account `stsmarttrafficweb5414`.

Azure Static Web Apps could not be deployed because the Azure for Students subscription restricts resource creation to regions that are not supported by Azure Static Web Apps. Therefore, Azure Storage Static Website hosting is used for the React frontend.

## Project structure

```
smart-traffic-monitoring-analytics-dashboard/
├── frontend/          React dashboard
├── backend/           Azure Functions API
├── data/              Simulated sample readings
├── docs/              Architecture, API, deployment, viva, and report
├── .github/workflows/ GitHub Actions build and deploy
├── README.md
└── LICENSE
```

## Local setup

Frontend:

```powershell
cd frontend
copy .env.example .env
npm install
npm run dev
```

Backend, from a second terminal:

```powershell
cd backend
copy local.settings.json.example local.settings.json
python -m pip install -r requirements.txt
func start
```

The dashboard uses `VITE_API_BASE_URL`. If that variable is missing, it calls `http://localhost:7071/api`.

`func start` needs [Azure Functions Core Tools](https://learn.microsoft.com/azure/azure-functions/functions-run-local). Leave `COSMOS_ENDPOINT` and `COSMOS_KEY` empty to use the local JSON store. The API still performs the real congestion, analytics, prediction, and simulation logic.

Python 3.11 is the recommended Function App runtime. The calculation code also runs on newer Python versions for unit tests.

Backend checks:

```powershell
cd backend
python generate_sample_data.py
python -m unittest discover -s tests -v
```

## Azure setup

Deployment requires your own Azure subscription. The steps are in [docs/azure-deployment.md](docs/azure-deployment.md). Do not paste keys into chat or commit them.

After the demo, delete the resource group `rg-smart-traffic-dashboard` if you no longer need it. Cosmos DB, Functions, and the storage accounts can create charges. Do not assume every service stays free.

## GitHub setup

```powershell
git branch -M main
gh repo create smart-traffic-monitoring-analytics-dashboard --public --source=. --remote=origin
git push -u origin main
```

If GitHub CLI is not signed in, create an empty repository named `smart-traffic-monitoring-analytics-dashboard` on GitHub and then run:

```powershell
git remote add origin https://github.com/<your-username>/smart-traffic-monitoring-analytics-dashboard.git
git push -u origin main
```

## Environment variables

Backend, in `backend/local.settings.json` locally and in the Function App configuration on Azure:

| Name | Purpose |
| --- | --- |
| `COSMOS_ENDPOINT` | Cosmos DB account URI |
| `COSMOS_KEY` | Cosmos DB primary key |
| `COSMOS_DATABASE` | Database name, default `TrafficDB` |
| `COSMOS_CONTAINER` | Container name, default `TrafficData` |

Frontend:

| Name | Purpose |
| --- | --- |
| `VITE_API_BASE_URL` | Functions base URL, including `/api` |

GitHub Actions secrets, stored in the repository settings and not in files:

| Name | Purpose |
| --- | --- |
| `AZURE_FUNCTIONAPP_NAME` | Function App name |
| `AZURE_FUNCTIONAPP_PUBLISH_PROFILE` | Function App publish profile |
| `AZURE_STORAGE_ACCOUNT` | Frontend storage account name |
| `AZURE_STORAGE_KEY` | Key used only to upload the static website |
| `VITE_API_BASE_URL` | Public Functions URL used while building the frontend |

These GitHub Actions secrets are stored for this repository. Their values are not in the source:

- `AZURE_FUNCTIONAPP_NAME`
- `AZURE_FUNCTIONAPP_PUBLISH_PROFILE`
- `AZURE_STORAGE_ACCOUNT`
- `AZURE_STORAGE_KEY`
- `VITE_API_BASE_URL`

Leave the repository variable `DEPLOY_TO_AZURE` unset. The workflow still runs tests and the frontend build. It skips both deploy jobs until that variable is `true`. The frontend job uploads `frontend/dist` to the `$web` container. The Functions job can replace the working API package, so turn the variable on only when that redeploy is intended.

## API endpoints

| Method | URL | Purpose |
| --- | --- | --- |
| GET | `/api/traffic` | Latest readings and history |
| GET | `/api/traffic/{location_id}` | One location |
| GET | `/api/traffic/analytics` | Summary analytics |
| GET | `/api/traffic/prediction` | Moving-average prediction |
| POST | `/api/traffic/simulate` | Append a simulated update |
| GET | `/api/health` | API and storage check |

Details and examples are in [docs/api-documentation.md](docs/api-documentation.md).

## Testing

Test cases for the dashboard, APIs, congestion, simulation, prediction, and error handling are in [docs/testing.md](docs/testing.md).

## Professor demo flow

1. Open the dashboard.
2. Show the six locations: MG Road, Silk Board, Electronic City, Whitefield, Marathahalli, and Hebbal.
3. Explain vehicle count, average speed, and road capacity in the table.
4. Explain congestion percentage as vehicles divided by road capacity.
5. Click **Simulate Traffic Update**.
6. Show the vehicle counts, charts, and status badges change.
7. Show the analytics cards, including the busiest and highest-congestion locations.
8. Show **Short-Term Traffic Prediction** and say the method is a moving average.
9. Explain the path: browser, Azure Storage static website, React dashboard, Azure Functions, Azure Cosmos DB.
10. Open the GitHub repository and, after deployment, the Azure resource group.

Say clearly that the readings are simulated for the academic demo.

## Limitations

- Readings are simulated. There is no CCTV, sensor, or live traffic-provider connection.
- Prediction is a moving average, not machine learning.
- The API reads the whole Cosmos container. That is acceptable for this small dataset.
- Authentication is intentionally simple. The college demo uses anonymous HTTP functions.
- The public dashboard is an Azure Storage static website. Azure Static Web Apps could not be deployed because the Azure for Students subscription restricts resource creation to regions that are not supported by Azure Static Web Apps.

## Future enhancements

These are ideas only. They are not implemented.

- Real IoT traffic sensors
- CCTV computer vision and vehicle detection
- GPS data and external traffic APIs
- Machine learning forecasts
- Traffic signal optimization
- Accident detection
- Route recommendations
- A mobile application
- Real-time alerts

## Conclusion

The project shows a complete academic path from simulated traffic readings to cloud storage, an HTTP API, congestion analytics, a simple prediction, and a dashboard. It is small enough to explain in a viva and structured so Azure and GitHub can host it.

## Documentation

- [Architecture](docs/architecture.md)
- [Implementation](docs/implementation.md)
- [API](docs/api-documentation.md)
- [Azure deployment](docs/azure-deployment.md)
- [Testing](docs/testing.md)
- [Viva preparation](docs/viva-preparation.md)
- [Project report](docs/project-report.md)
