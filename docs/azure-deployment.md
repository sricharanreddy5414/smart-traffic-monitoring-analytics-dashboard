# Azure deployment

The backend and the public website are deployed. Traffic readings in Cosmos DB are simulated academic data, not live sensor data.

Azure Static Web Apps could not be deployed because the Azure for Students subscription restricts resource creation to regions that are not supported by Azure Static Web Apps. Therefore, Azure Storage Static Website hosting is used for the React frontend.

## Current deployment

Subscription: Azure for Students. Tenant: Alliance University. Region used: Central India. That region is allowed by the subscription policy and supports Cosmos DB and Linux Functions.

| Resource | Name | Region |
| --- | --- | --- |
| Resource group | `rg-smart-traffic-dashboard` | Central India |
| Cosmos DB account | `cosmos-smart-traffic` | Central India, serverless |
| Database | `TrafficDB` | |
| Container | `TrafficData` | Partition key `/location_id` |
| Function App | `func-smart-traffic-dashboard` | Central India, Linux, Python 3.11, Consumption |
| Function API | `https://func-smart-traffic-dashboard.azurewebsites.net/api` | |
| Function App storage | `stsmarttraffic5414` | Central India, Standard LRS. Required by Functions. Not the public website |
| Frontend storage account | `stsmarttrafficweb5414` | Central India, Standard LRS, static website enabled |
| Frontend URL | `https://stsmarttrafficweb5414.z29.web.core.windows.net/` | Index and 404 document: `index.html` |

Verified API behaviour:

- `GET /api/health` returns `storage_mode` `cosmos-db` and `data_source` `simulated`.
- `GET /api/traffic`, `GET /api/traffic/analytics`, `GET /api/traffic/prediction`, and `GET /api/traffic/LOC001` return the simulated Bengaluru locations.
- `POST /api/traffic/simulate` appends one new simulated reading per location.
- The public website loads those responses, draws the charts and table, calculates congestion, refreshes, and can simulate an update that is stored in Cosmos DB.

The container was seeded once from `data/sample_traffic_data.json` (78 readings). Later simulation added more readings. Do not run the seeder again.

Function App settings `COSMOS_ENDPOINT`, `COSMOS_KEY`, `COSMOS_DATABASE`, and `COSMOS_CONTAINER` are stored in Azure application settings. They are not in source code. `COSMOS_DATABASE` is `TrafficDB`. `COSMOS_CONTAINER` is `TrafficData`.

Platform CORS allows:

- `https://stsmarttrafficweb5414.z29.web.core.windows.net`
- `http://localhost:5173`
- `http://localhost:4173`
- `http://127.0.0.1:5173`
- `http://127.0.0.1:4173`

Do not switch this list to `*`.

### Why the frontend is a Storage static website

Azure Static Web Apps was not created. Creation was rejected in every relevant region, and no Static Web App resource was left behind.

The subscription policy allows only Malaysia West, Southeast Asia, Austria East, UAE North, and Central India. Azure Static Web Apps can be created only in Central US, East US 2, West US 2, West Europe, and East Asia. There is no region that satisfies both.

The public dashboard is the static website on `stsmarttrafficweb5414`. The Function App storage account `stsmarttraffic5414` was not changed.

GitHub repository: `https://github.com/sricharanreddy5414/smart-traffic-monitoring-analytics-dashboard`

Workflow: `.github/workflows/azure-deploy.yml`. The latest run on `main` completed the test job. Deploy jobs did not run.

These Actions secrets exist and are not written in the repository:

- `AZURE_FUNCTIONAPP_NAME`
- `AZURE_FUNCTIONAPP_PUBLISH_PROFILE`
- `AZURE_STORAGE_ACCOUNT`
- `AZURE_STORAGE_KEY`
- `VITE_API_BASE_URL` = `https://func-smart-traffic-dashboard.azurewebsites.net/api`

The repository variable `DEPLOY_TO_AZURE` is not set. Leave it unset unless a push should publish both the Function App and the static website. The Functions deploy job can replace the working package, which currently includes the Linux Python dependencies the remote build did not install. The frontend job uploads `frontend/dist` to the `$web` container.

The sections below are the original setup notes. The names above are the ones that were actually created.

Use the Azure portal for the main path. Azure CLI commands are included where they save time. Resource names that Azure must keep unique need a suffix.

Suggested names:

| Resource | Suggested name |
| --- | --- |
| Resource group | `rg-smart-traffic-dashboard` |
| Cosmos DB account | `cosmos-smart-traffic-<unique>` |
| Function App | `func-smart-traffic-dashboard-<unique>` |
| Static Web App | `stapp-smart-traffic-dashboard-<unique>` |

Prefer student-friendly settings: Consumption plan for Functions, serverless Cosmos DB, and the Free tier for Static Web Apps if it is available. These choices can still create charges. After the evaluation, delete the resource group if you do not need the demo anymore.

Do not paste the Cosmos key, publish profile, or deployment token into chat, into Git, or into a screenshot you will publish.

## 1. Sign in to Azure

1. Open [https://portal.azure.com](https://portal.azure.com).
2. Sign in with your college or personal Azure account.
3. Confirm the subscription you want to use. The portal shows it in the top bar or under Subscriptions.

CLI alternative:

```powershell
az login
az account set --subscription "<subscription-name-or-id>"
```

## 2. Create a resource group

1. Search for **Resource groups**.
2. Select **Create**.
3. Subscription: your subscription.
4. Resource group: `rg-smart-traffic-dashboard`.
5. Region: a nearby region, for example Central India.
6. Review and create.

```powershell
az group create --name rg-smart-traffic-dashboard --location centralindia
```

## 3. Create Cosmos DB

1. Search for **Azure Cosmos DB**.
2. Select **Create**.
3. Choose **Azure Cosmos DB for NoSQL**.
4. Resource group: `rg-smart-traffic-dashboard`.
5. Account name: `cosmos-smart-traffic-<unique>`. The name must be unique across Azure.
6. Capacity mode: **Serverless** for a short academic demo.
7. Region: the same region as the resource group when it is offered.
8. Review and create. Wait until deployment finishes.

```powershell
az cosmosdb create --name cosmos-smart-traffic-<unique> --resource-group rg-smart-traffic-dashboard --locations regionName=centralindia --capabilities EnableServerless
```

## 4. Create the database

1. Open the Cosmos DB account.
2. Open **Data Explorer**.
3. Select **New Database**.
4. Database id: `TrafficDB`.
5. Create.

```powershell
az cosmosdb sql database create --account-name cosmos-smart-traffic-<unique> --resource-group rg-smart-traffic-dashboard --name TrafficDB
```

## 5. Create the container

1. In Data Explorer, open `TrafficDB`.
2. Select **New Container**.
3. Container id: `TrafficData`.
4. Partition key: `/location_id`.
5. Create.

```powershell
az cosmosdb sql container create --account-name cosmos-smart-traffic-<unique> --resource-group rg-smart-traffic-dashboard --database-name TrafficDB --name TrafficData --partition-key-path "/location_id"
```

## 6. Create the Azure Function App

1. Search for **Function App** and select **Create**.
2. Resource group: `rg-smart-traffic-dashboard`.
3. Name: `func-smart-traffic-dashboard-<unique>`.
4. Runtime: **Python**.
5. Version: **3.11**.
6. Operating system: Linux.
7. Plan: **Consumption**.
8. Region: the same region as the other resources when possible.
9. Review and create.

```powershell
az functionapp create --resource-group rg-smart-traffic-dashboard --consumption-plan-location centralindia --runtime python --runtime-version 3.11 --functions-version 4 --name func-smart-traffic-dashboard-<unique> --os-type Linux --storage-account <unique-storage-name>
```

The CLI command also needs a Storage account because the Functions host uses it. The portal creates one for you during Function App creation. You do not need to build a second application on that storage account.

## 7. Configure Function App environment variables

1. Open the Function App.
2. Open **Environment variables** or **Configuration**.
3. Add:

| Name | Value |
| --- | --- |
| `COSMOS_ENDPOINT` | URI from the Cosmos DB account **Keys** page |
| `COSMOS_KEY` | Primary key from that same page |
| `COSMOS_DATABASE` | `TrafficDB` |
| `COSMOS_CONTAINER` | `TrafficData` |

4. Save. Restart the Function App if the portal asks you to.

Also open the Function App **CORS** page and allow the real frontend origin. The current deployment allows the local dashboard origins listed at the top of this file. Do not use `*` as the platform CORS list. Do not put the key in frontend settings.

CLI shape, without placing a real key in the repository:

```powershell
az functionapp config appsettings set --name func-smart-traffic-dashboard-<unique> --resource-group rg-smart-traffic-dashboard --settings COSMOS_DATABASE=TrafficDB COSMOS_CONTAINER=TrafficData COSMOS_ENDPOINT="<paste-in-your-terminal>" COSMOS_KEY="<paste-in-your-terminal>"
```

## 8. Deploy the backend

Portal path using GitHub is covered in the GitHub section below. A direct CLI publish from your machine:

```powershell
cd backend
mkdir data
copy ..\data\sample_traffic_data.json data\sample_traffic_data.json
func azure functionapp publish func-smart-traffic-dashboard-<unique>
```

The copy step matters. The Function App package is the `backend` folder, while the sample file in Git is stored at `data/sample_traffic_data.json`. The API looks in both places. The GitHub Action copies the file before it deploys.

The first API call to an empty container inserts the sample readings.

## 9. Test the backend API

Open this URL in a browser, using your Function App name:

```
https://func-smart-traffic-dashboard-<unique>.azurewebsites.net/api/traffic
```

You should see JSON with six locations and `"data_source": "simulated"`. Then try:

```
https://<function-app>.azurewebsites.net/api/traffic/analytics
https://<function-app>.azurewebsites.net/api/traffic/prediction
https://<function-app>.azurewebsites.net/api/health
```

If the response says it cannot connect to Cosmos DB, check the four environment variables and confirm the container partition key is `/location_id`.

## 10. Host the frontend on a Storage static website

Azure Static Web Apps could not be deployed because the Azure for Students subscription restricts resource creation to regions that are not supported by Azure Static Web Apps. Therefore, Azure Storage Static Website hosting is used for the React frontend.

The website account for this project is `stsmarttrafficweb5414` in `rg-smart-traffic-dashboard`, Central India, Standard LRS. Static website hosting is enabled with `index.html` as both the index document and the error document. The built files from `frontend/dist` are uploaded to the `$web` container, with `index.html` at the root.

Do not enable static website hosting on `stsmarttraffic5414`. That account belongs to the Function App.

## 11. Connect the GitHub repository

The repository is `https://github.com/sricharanreddy5414/smart-traffic-monitoring-analytics-dashboard` on branch `main`.

This repository already has `.github/workflows/azure-deploy.yml`. Do not add a second workflow from the Azure portal.

## 12. Configure frontend environment variables

Vite reads `VITE_API_BASE_URL` when the frontend is built. Set it to the Function App API root, including `/api`:

```
https://func-smart-traffic-dashboard-<unique>.azurewebsites.net/api
```

Store it as a GitHub Actions secret named `VITE_API_BASE_URL`. Do not commit a `.env` file that contains this if you treat the URL as private. The URL itself is not a password, but the production value should be injected at build time.

Also add these GitHub secrets:

| Secret | Where to copy it from |
| --- | --- |
| `AZURE_STORAGE_ACCOUNT` | Frontend storage account name |
| `AZURE_STORAGE_KEY` | Storage account access key. Store it as a secret. Do not commit it |
| `AZURE_FUNCTIONAPP_NAME` | The Function App name |
| `AZURE_FUNCTIONAPP_PUBLISH_PROFILE` | Function App publish profile. Paste the whole file contents into the secret |
| `VITE_API_BASE_URL` | `https://func-smart-traffic-dashboard.azurewebsites.net/api` |

The repository variable `DEPLOY_TO_AZURE` stays unset until a push should publish the Function App and the static website.

## 13. Deploy the frontend

Push to `main`, or run the **Build and Azure Deploy** workflow from the GitHub Actions tab. The workflow:

1. Runs backend unit tests.
2. Builds the frontend.
3. If `DEPLOY_TO_AZURE` is `true`, publishes the Function App and uploads the frontend to the Azure Storage static website.

Open `https://stsmarttrafficweb5414.z29.web.core.windows.net/`.

## 14. Test the complete application

1. The dashboard title is Smart Traffic Monitoring and Analytics Dashboard.
2. Six locations appear and the summary numbers match the table.
3. Refresh Data reloads the page data.
4. Simulate Traffic Update changes values and the charts.
5. Prediction shows Moving Average.
6. Stop the Function App and refresh the dashboard. The page should show `Unable to retrieve traffic data.` instead of a blank crash.
7. Start the Function App again before the viva.

## Recorded resource names

Do not record keys here.

| Resource | Final name | Region |
| --- | --- | --- |
| Resource group | `rg-smart-traffic-dashboard` | Central India |
| Cosmos DB account | `cosmos-smart-traffic` | Central India |
| Database / container | `TrafficDB` / `TrafficData` | Partition key `/location_id` |
| Function App | `func-smart-traffic-dashboard` | Central India |
| Function API URL | `https://func-smart-traffic-dashboard.azurewebsites.net/api` | |
| Function App storage | `stsmarttraffic5414` | Central India |
| Frontend storage account | `stsmarttrafficweb5414` | Central India |
| Frontend URL | `https://stsmarttrafficweb5414.z29.web.core.windows.net/` | Static website |
| Static Web App | Not created | Region policy blocks every Static Web Apps region |

## Cost and cleanup

These resources are running and can create charges: resource group `rg-smart-traffic-dashboard`, serverless Cosmos DB account `cosmos-smart-traffic`, Consumption Function App `func-smart-traffic-dashboard`, Function App storage `stsmarttraffic5414`, and frontend storage `stsmarttrafficweb5414`. There is no Static Web App. This is not a promise that the bill will be zero. When the evaluation is over, delete the whole resource group. That removes the database, the API, and both storage accounts. Do not delete other resource groups in the subscription:

1. Open the resource group.
2. Select **Delete resource group**.
3. Type the resource group name to confirm.

```powershell
az group delete --name rg-smart-traffic-dashboard --yes
```

Deleting the group removes the database, the API, and the website.
