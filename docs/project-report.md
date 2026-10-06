# Project report

## 1. Title

Smart Traffic Monitoring and Analytics Dashboard

## 2. Abstract

This mini project presents a cloud-style traffic monitoring dashboard for six Bengaluru locations: MG Road, Silk Board, Electronic City, Whitefield, Marathahalli, and Hebbal. The system stores traffic readings, calculates congestion from vehicle count and road capacity, summarizes analytics, and estimates the next vehicle count with a moving average. A React dashboard shows the results. The intended cloud deployment uses Azure Static Web Apps, Azure Functions, and Azure Cosmos DB. The traffic readings are simulated for academic demonstration so the project can be evaluated without claiming access to live cameras or road sensors.

## 3. Introduction

Traffic management depends on seeing how full a road is, not only on a single vehicle count. A count of 450 vehicles means something different on a road that can hold 600 vehicles than on a road that can hold 300. This project combines count, speed, and capacity, then presents congestion in a form that can be explained in a project review.

The work is limited to a college mini project. It uses one website, one HTTP API, and one database.

## 4. Problem statement

Urban traffic congestion increases due to inefficient monitoring and lack of predictive analytics. The required system is a cloud-hosted traffic monitor that collects traffic data, performs analytics, and visualizes congestion patterns.

## 5. Objectives

- Represent traffic at six fixed locations with a consistent data model.
- Store the readings in Azure Cosmos DB.
- Provide HTTP APIs with Azure Functions.
- Calculate congestion, summary analytics, and a short-term prediction.
- Visualize the results on a dashboard.
- Provide a simulation control for demonstration.
- Document deployment, testing, and viva answers.

## 6. Existing system

A manual or spreadsheet approach can list vehicle counts, but it does not offer an API, a shared cloud store, or a repeatable congestion rule. Public maps show traffic to drivers, yet a student cannot honestly claim those feeds as their own backend. This project therefore uses simulated readings and makes that limitation visible in the interface and the report.

## 7. Proposed system

The proposed system is a dashboard plus an API. The API stores readings, calculates congestion with a published formula, and returns analytics and a moving-average prediction. Users refresh the view or append a simulated update. When Azure credentials are configured, Cosmos DB is the store. Before that, a local JSON file lets the same API be demonstrated.

## 8. System architecture

The user opens the React dashboard. Static Web Apps hosts that dashboard. The browser calls Azure Functions. Functions reads Cosmos DB and runs the analytics engine. The engine calculates congestion, prepares the time series, and computes the moving average. The dashboard then draws cards, charts, a table, and a schematic map.

```
User -> React Dashboard -> Azure Static Web Apps -> Azure Functions
     -> Azure Cosmos DB -> Analytics -> Dashboard
```

## 9. Technologies used

- Frontend: React, Vite, JavaScript, HTML, CSS, Recharts
- Backend: Python and Azure Functions
- Database: Azure Cosmos DB
- Hosting: Azure Static Web Apps
- Source control: GitHub
- Automation: GitHub Actions

## 10. Hardware and software requirements

Hardware: a computer that can run a browser and the local development tools.

Software:

- A current web browser
- Node.js and npm for the frontend
- Python 3.11 recommended for the Function App
- Azure Functions Core Tools for `func start`
- An Azure subscription for cloud deployment
- Git and a GitHub account

The local JSON mode does not need a Cosmos DB account until the cloud demonstration.

## 11. System modules

| Module | Role |
| --- | --- |
| Dashboard | Displays traffic, charts, map, and prediction |
| API layer | Serves JSON over HTTP |
| Data store | Cosmos DB, or a local JSON file before Azure is configured |
| Congestion module | Applies the percentage formula and status bands |
| Analytics module | Summarizes the latest reading at each location |
| Prediction module | Moving average of recent vehicle counts |
| Simulation module | Writes one new realistic reading per location |

## 12. Traffic data collection

Collection in this version is simulated. `data/sample_traffic_data.json` holds half-hour readings for the six locations. The file is identified as academic simulation data. A future version could accept the same fields from sensors or another API without changing the dashboard contract.

## 13. Traffic analytics

From the latest reading at each location, the API calculates total vehicles, average speed, average congestion, the number of congested locations, the busiest location, the least busy location, and the highest and lowest congestion locations. The dashboard cards read these values from the API.

## 14. Congestion detection

Congestion percentage is vehicle count divided by road capacity, multiplied by 100. The status is LOW up to 40, MEDIUM from 41 to 65, HIGH from 66 to 85, and CRITICAL from 86 upward. A location counts as congested when the percentage is above 65. The sample MG Road reading, 450 vehicles and capacity 600, is 75 percent and HIGH.

## 15. Predictive analytics

The prediction method is a moving average. The API takes up to five recent vehicle counts for a location and averages them. A documented example is 400, 430, 450, 470, and 460, which predicts 442. The dashboard titles this section Short-Term Traffic Prediction and names the method Moving Average. No machine learning model is trained.

## 16. Cloud implementation

The design uses one resource group, one Cosmos DB account, one Function App, and one Static Web App. GitHub Actions can deploy the Function App and the Static Web App after repository secrets are stored. Cloud resources are created by the student in Azure. They are not created merely by cloning this repository.

## 17. Database

Database name: `TrafficDB`. Container name: `TrafficData`. Partition key: `/location_id`. Each document is one reading. The connection values are `COSMOS_ENDPOINT`, `COSMOS_KEY`, `COSMOS_DATABASE`, and `COSMOS_CONTAINER`.

## 18. API layer

The API provides traffic collection reads, a single-location read, analytics, prediction, and simulation. Unknown locations return 404. Invalid request bodies return 400. Database connection trouble returns 503. The frontend shows a clear error if the API is down.

## 19. Dashboard

The dashboard has a header, five summary cards, a vehicle-count line chart, a speed bar chart, congestion charts, a prediction table, a schematic location view, and a traffic table. Colors follow the status bands: green, yellow, orange, and red. Refresh Data and Simulate Traffic Update both call the API.

## 20. Testing

Unit tests check the congestion example, status boundaries, analytics, the moving-average example, simulation limits, API handlers, validation, and the local JSON store. Manual tests cover opening the dashboard, the traffic API, simulation, prediction, an invalid location, and a stopped backend. The test list is in `docs/testing.md`.

## 21. Results

On the generated sample, the latest totals are 2,520 vehicles across six locations. Three locations are congested under the HIGH or CRITICAL rule. Silk Board is the busiest and the most congested in that sample. Whitefield is the least busy and the least congested. MG Road at 450 vehicles and capacity 600 is 75 percent, HIGH. These figures are properties of the simulated dataset, and they change after Simulate Traffic Update.

## 22. Advantages

- The congestion rule is visible and repeatable.
- The same API works locally and is structured for Azure.
- The dashboard can be demonstrated without special hardware.
- The source, tests, and deployment workflow are in one repository.
- The project states clearly that the data is simulated.

## 23. Limitations

- There is no live sensor, CCTV, or external traffic feed.
- The forecast is a short moving average.
- The college API does not include user accounts.
- Reading the full Cosmos container is acceptable only because the dataset is small.
- Azure deployment and any billing depend on the account used by the student.

## 24. Future enhancements

Real IoT sensors, CCTV computer vision, vehicle detection, GPS data, external traffic APIs, machine learning forecasts, traffic signal optimization, accident detection, route recommendations, a mobile application, and real-time alerts could be added later. They are outside this mini project.

## 25. Conclusion

The project implements a complete academic traffic dashboard: simulated collection, cloud-ready storage, an HTTP API, congestion detection, summary analytics, a moving-average prediction, and visualization. It is small enough to explain in a viva and concrete enough to run.

## 26. References

- Microsoft Learn, Azure Functions documentation: https://learn.microsoft.com/azure/azure-functions/
- Microsoft Learn, Azure Cosmos DB documentation: https://learn.microsoft.com/azure/cosmos-db/
- Microsoft Learn, Azure Static Web Apps documentation: https://learn.microsoft.com/azure/static-web-apps/
- React documentation: https://react.dev/
- Vite documentation: https://vite.dev/
- Recharts documentation: https://recharts.org/
- GitHub Actions documentation: https://docs.github.com/actions
