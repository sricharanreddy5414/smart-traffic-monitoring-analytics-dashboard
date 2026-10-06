# Testing

Run the automated checks from the backend folder:

```powershell
cd backend
python -m unittest discover -s tests -v
```

Frontend production build:

```powershell
cd frontend
npm install
npm run build
```

The cases below are the manual checks for a project evaluation.

## Test Case 1: Open dashboard

Steps:

1. Start the Functions host with `func start`.
2. Start the frontend with `npm run dev`.
3. Open the local site.

Expected: The dashboard loads. The title is Smart Traffic Monitoring and Analytics Dashboard. Six locations are visible. The page shows `Loading traffic data...` before the data arrives.

## Test Case 2: Get traffic API

Steps:

1. Open `http://localhost:7071/api/traffic`.

Expected: Valid JSON. `locations` has six items. Each item has vehicle count, speed, road capacity, congestion percentage, and status. `data_source` is `simulated`.

## Test Case 3: Calculate congestion

Steps:

1. Read the MG Road row in the sample data: 450 vehicles and road capacity 600.
2. Calculate `(450 / 600) * 100`.
3. Compare it with `GET /api/traffic/LOC001`.

Expected: The percentage is 75 and the status is HIGH.

## Test Case 4: Click Simulate Traffic Update

Steps:

1. Note the vehicle counts and the last updated time.
2. Click **Simulate Traffic Update**.

Expected: The API saves six new readings. The table, charts, congestion badges, and last updated time change. Counts stay realistic.

## Test Case 5: Prediction

Steps:

1. Open the Short-Term Traffic Prediction section.
2. Open `http://localhost:7071/api/traffic/prediction`.

Expected: The method is Moving Average. Each location shows the current vehicle count, the predicted count, and the recent counts used in the average.

## Test Case 6: Invalid location

Steps:

1. Open `http://localhost:7071/api/traffic/LOC999`.

Expected: HTTP 404 and a JSON error that says the location ID is invalid.

## Test Case 7: Backend unavailable

Steps:

1. Stop the Functions host.
2. Refresh the dashboard.

Expected: The page shows `Unable to retrieve traffic data.` It does not show a blank crashed page.

## Test Case 8: Refresh Data

Steps:

1. Click **Refresh Data** while the API is running.

Expected: The dashboard reloads from the API. The button shows a busy label while the request is in progress.

## Test Case 9: Automatic refresh

Steps:

1. Leave automatic refresh enabled.
2. Clear the checkbox.

Expected: The header shows `LIVE MONITORING: ON` while the checkbox is selected and `LIVE MONITORING: OFF` after it is cleared. The timer polls every 10 seconds. It does not simulate new readings by itself.

## Test Case 10: Empty data

Steps:

1. Point a temporary local store at an empty JSON array and call the traffic handler, or inspect the unit test `test_empty_database`.

Expected: The API returns an empty location list. The dashboard shows `No traffic data available.`

## Test Case 11: Invalid simulate body

Steps:

1. POST plain text to `/api/traffic/simulate` with content type JSON that is not valid, or run the unit test.

Expected: HTTP 400 and an error that says the body must be valid JSON.

## Test Case 12: Responsive layout

Steps:

1. Narrow the browser to a phone width and back to a desktop width.

Expected: Cards, charts, the map, and the table remain readable. The table scrolls sideways instead of cutting off columns.
