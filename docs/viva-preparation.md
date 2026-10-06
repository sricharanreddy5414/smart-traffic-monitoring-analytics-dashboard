# Viva preparation

Answer in two or three sentences. If the examiner asks for a formula or an example, use the numbers below.

## 1. What is the project?

It is a cloud-based Smart Traffic Monitoring and Analytics Dashboard. It stores traffic readings, calculates congestion and a short-term prediction, and shows the result for six Bengaluru locations.

## 2. What problem does it solve?

Cities struggle to see where congestion is building because monitoring and simple prediction are missing. This project demonstrates a path from traffic readings to storage, analytics, and a dashboard.

## 3. Why did you select this topic?

It fits the SIH Smart Transportation theme and uses a small set of cloud services that a college project can actually implement: a website, an API, and a database.

## 4. Why is traffic monitoring important?

If planners can see vehicle count, speed, and congestion together, they can tell which junction is overloaded. The same data can later support signals, alerts, or routing.

## 5. What is cloud computing?

Cloud computing means using computing services over the internet instead of only on one local computer. In this project the website, API, and database can run on Microsoft Azure.

## 6. Why did you use Azure?

The project needs hosting, a serverless API, and a document database. Azure Static Web Apps, Azure Functions, and Azure Cosmos DB match those three roles.

## 7. What is Azure Functions?

Azure Functions runs a small piece of code when an HTTP request arrives. I do not manage a server process myself. The Python file `function_app.py` defines the traffic APIs.

## 8. What is serverless computing?

Serverless means the cloud provider runs the code on demand and I pay for use rather than for a virtual machine that stays on all day. Azure Functions is the serverless part of this project.

## 9. What is Cosmos DB?

Azure Cosmos DB is a NoSQL database. This project stores each traffic reading as a JSON document in the `TrafficData` container.

## 10. Why use Cosmos DB?

Traffic readings are documents with a location, time, and measurements. Cosmos DB stores that shape directly, and the partition key `/location_id` groups readings for one junction.

## 11. What is Azure Static Web Apps?

It hosts the built React files and gives the dashboard a public HTTPS address. The API stays in the Function App. The Static Web App does not calculate congestion.

## 12. What is GitHub?

GitHub stores the Git repository online so the project has version history and can be shown during evaluation. The repository name is `smart-traffic-monitoring-analytics-dashboard`.

## 13. What is GitHub Actions?

GitHub Actions runs commands automatically when code is pushed. This project uses it to run unit tests, build the frontend, and optionally deploy to Azure.

## 14. What is CI/CD?

CI means continuous integration: every change is built and tested. CD means continuous delivery: a successful `main` branch can be deployed. Deployment runs only after the `DEPLOY_TO_AZURE` setting and the GitHub secrets are in place.

## 15. What is an API?

An API is a way for one program to request data from another. The React dashboard does not read the database itself. It calls the Functions API.

## 16. What is a REST API?

This project uses HTTP methods and URLs. GET reads traffic, analytics, and prediction. POST creates a simulated update. Responses are JSON, with status codes such as 200, 400, and 404.

## 17. How does the frontend communicate with the backend?

`frontend/src/services/api.js` calls `VITE_API_BASE_URL`, which is `http://localhost:7071/api` in local development. The dashboard requests traffic, analytics, and prediction, then renders those JSON responses.

## 18. How is traffic data stored?

Each reading is one record with an id, location, timestamp, vehicle count, average speed, road capacity, latitude, and longitude. On Azure it is a Cosmos DB item. Locally, if credentials are empty, the same records are stored in a JSON file.

## 19. How is congestion calculated?

`congestion percentage = (vehicle count / road capacity) × 100`. For 450 vehicles and a capacity of 600, that is 75 percent. 0–40 is LOW, 41–65 is MEDIUM, 66–85 is HIGH, and 86 or more is CRITICAL, so 75 is HIGH.

## 20. What is predictive analytics?

Predictive analytics uses existing observations to estimate a near-future value. This project estimates the next vehicle count. It does not claim to forecast a whole city.

## 21. How does your prediction work?

It uses a moving average of recent vehicle counts for that location. It is basic academic predictive analytics, not a machine learning model.

## 22. What is a moving average?

A moving average is the mean of a recent window of values. For 400, 430, 450, 470, and 460, the average is `(400 + 430 + 450 + 470 + 460) / 5 = 442`.

## 23. Is your traffic data real?

No. Traffic data is simulated for academic demonstration. The architecture can later be connected to IoT sensors, CCTV or computer vision, GPS feeds, or an external traffic API.

## 24. How does the simulation work?

The Simulate Traffic Update button reads the latest values, changes vehicle count by about -30 to +30, changes speed slightly, recalculates congestion, and saves a new reading for all six locations. The dashboard then reloads.

## 25. How does the system scale?

Azure Functions can run more request handlers as calls increase, and Cosmos DB partitions data by location. This mini project stores a small simulated dataset, so the API reads the container directly. A larger system would query a narrower time range.

## 26. What happens if traffic increases?

Vehicle count goes up, so the congestion percentage goes up. The status can move from MEDIUM to HIGH or CRITICAL. The speed in the simulation also tends to fall when the vehicle count jumps.

## 27. What are the limitations?

The data is simulated, the prediction is only a moving average, there is no login system, and there is no live sensor feed. Azure resources also need to be created in the student's own subscription before the public demo works.

## 28. What are future enhancements?

Possible next steps are IoT sensors, CCTV vehicle detection, GPS or external traffic APIs, a real forecasting model, signal timing, accident detection, route suggestions, a mobile app, and alerts. None of those are implemented in this version.

## 29. Explain the architecture.

The user opens the React dashboard on Azure Static Web Apps. The dashboard calls Azure Functions. Functions reads Azure Cosmos DB, calculates congestion, trends, and the moving average, and returns JSON. The dashboard draws the cards, charts, table, and map.

## 30. What Azure services did you use?

Azure Static Web Apps hosts the frontend. Azure Functions hosts the Python API. Azure Cosmos DB stores the readings. A resource group holds those resources. GitHub Actions deploys them after secrets are configured.

## 31. Why is the partition key location_id?

Most lookups are for one junction or for the latest reading grouped by junction. `/location_id` keeps one location's documents together.

## 32. What does LIVE MONITORING mean on the page?

It means the dashboard is polling the API every 10 seconds. It does not mean a camera or sensor is connected. The checkbox turns that polling off.
