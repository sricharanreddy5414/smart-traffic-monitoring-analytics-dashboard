# Azure deployment

Implementation of the application is in this repository. Deployment requires the student's Azure account and configuration. Creating the files does not create Azure resources and does not mean the site is already online.

Use the Azure portal for the main path. Azure CLI commands are included where they save time. Resource names that Azure must keep unique need a suffix. Write the final names in the table at the end of this file after you create them.

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

Also open the Function App **CORS** page and allow the Static Web App origin. During early testing you can allow `*` and tighten it later. Do not put the key in frontend settings.

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

## 10. Create the Azure Static Web App

1. Search for **Static Web Apps** and select **Create**.
2. Resource group: `rg-smart-traffic-dashboard`.
3. Name: `stapp-smart-traffic-dashboard-<unique>`.
4. Plan: Free, if available.
5. Source: GitHub. Sign in and choose this repository and the `main` branch.
6. Build presets: Custom.
7. App location: `frontend`.
8. Api location: leave empty. The API is the separate Function App.
9. Output location: `dist`.
10. Review and create.

If you prefer to deploy only after tests pass, skip the portal's automatic workflow and use the workflow already stored in `.github/workflows/azure-deploy.yml`.

## 11. Connect the GitHub repository

1. Create the GitHub repository `smart-traffic-monitoring-analytics-dashboard` if it does not exist.
2. Push the `main` branch.
3. In the Static Web App, open **Manage deployment token** only when you are ready to store it as a GitHub secret.

The portal can add a workflow by itself. This repository already has `.github/workflows/azure-deploy.yml`. If the portal creates a second workflow file, keep one of them so two jobs do not deploy at the same time.

## 12. Configure frontend environment variables

Vite reads `VITE_API_BASE_URL` when the frontend is built. Set it to the Function App API root, including `/api`:

```
https://func-smart-traffic-dashboard-<unique>.azurewebsites.net/api
```

Store it as a GitHub Actions secret named `VITE_API_BASE_URL`. Do not commit a `.env` file that contains this if you treat the URL as private. The URL itself is not a password, but the production value should be injected at build time.

Also add these GitHub secrets:

| Secret | Where to copy it from |
| --- | --- |
| `AZURE_STATIC_WEB_APPS_API_TOKEN` | Static Web App, Manage deployment token |
| `AZURE_FUNCTIONAPP_NAME` | The Function App name |
| `AZURE_FUNCTIONAPP_PUBLISH_PROFILE` | Function App, Get publish profile. Paste the whole file contents into the secret |
| `VITE_API_BASE_URL` | `https://<function-app>.azurewebsites.net/api` |

Then create a GitHub repository **variable** (not a secret) named `DEPLOY_TO_AZURE` and set it to `true`.

## 13. Deploy the frontend

Push to `main`, or run the **Build and Azure Deploy** workflow from the GitHub Actions tab. The workflow:

1. Runs backend unit tests.
2. Builds the frontend.
3. If `DEPLOY_TO_AZURE` is `true`, publishes the Function App and the Static Web App.

Open the Static Web App URL shown in the Azure portal.

## 14. Test the complete application

1. The dashboard title is Smart Traffic Monitoring and Analytics Dashboard.
2. Six locations appear and the summary numbers match the table.
3. Refresh Data reloads the page data.
4. Simulate Traffic Update changes values and the charts.
5. Prediction shows Moving Average.
6. Stop the Function App and refresh the dashboard. The page should show `Unable to retrieve traffic data.` instead of a blank crash.
7. Start the Function App again before the viva.

## Record your resource names

Fill this in after creation. Do not record keys here.

| Resource | Final name | Region |
| --- | --- | --- |
| Resource group | | |
| Cosmos DB account | | |
| Function App | | |
| Static Web App | | |
| Static Web App URL | | |
| Function App URL | | |

## Cost and cleanup

Serverless Cosmos DB, the Functions Consumption plan, and the Static Web Apps Free tier are reasonable for a short demo, but they are not a promise that the bill will be zero. A Cosmos DB account in provisioned throughput mode can cost more. Prefer serverless, and delete the resource group when the evaluation is over:

1. Open the resource group.
2. Select **Delete resource group**.
3. Type the resource group name to confirm.

```powershell
az group delete --name rg-smart-traffic-dashboard --yes
```

Deleting the group removes the database, the API, and the website.
