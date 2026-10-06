# API documentation

Base URL locally:

```
http://localhost:7071/api
```

After Azure deployment, replace the host with the Function App host. The path prefix remains `/api`.

All successful responses are JSON. Errors use this shape:

```json
{ "error": "Explanation of the problem." }
```

Traffic responses include `data_source: "simulated"` and a disclaimer. The readings are academic simulation data.

## GET /api/traffic

| | |
| --- | --- |
| Method | GET |
| URL | `/api/traffic` |
| Purpose | Return the latest reading for every location and the history used by charts |

Request: no body.

Response `200`:

```json
{
  "data_source": "simulated",
  "disclaimer": "Traffic data is simulated for academic demonstration. The architecture can later be connected to IoT sensors, CCTV/computer vision systems, GPS feeds, or external traffic APIs.",
  "storage_mode": "local-json",
  "last_updated": "2026-10-06T10:00:00Z",
  "locations": [
    {
      "id": "traffic-LOC001-20261006T100000Z",
      "location_id": "LOC001",
      "location_name": "MG Road",
      "timestamp": "2026-10-06T10:00:00Z",
      "vehicle_count": 450,
      "average_speed": 28,
      "road_capacity": 600,
      "latitude": 12.9756,
      "longitude": 77.6065,
      "congestion_percentage": 75.0,
      "congestion_status": "HIGH"
    }
  ],
  "history": []
}
```

`storage_mode` is `cosmos-db` when Cosmos DB credentials are configured. `history` contains the same fields for every stored reading.

If the store is empty, the status is still `200` and `locations` is an empty array.

## GET /api/traffic/{location_id}

| | |
| --- | --- |
| Method | GET |
| URL | `/api/traffic/LOC001` |
| Purpose | Return the latest reading and history for one known location |

Path parameter: `location_id`, for example `LOC001`.

Known IDs:

| ID | Location |
| --- | --- |
| LOC001 | MG Road |
| LOC002 | Silk Board |
| LOC003 | Electronic City |
| LOC004 | Whitefield |
| LOC005 | Marathahalli |
| LOC006 | Hebbal |

Response `200`:

```json
{
  "data_source": "simulated",
  "storage_mode": "local-json",
  "location": {
    "location_id": "LOC001",
    "location_name": "MG Road",
    "vehicle_count": 450,
    "road_capacity": 600,
    "congestion_percentage": 75.0,
    "congestion_status": "HIGH"
  },
  "history": []
}
```

Response `404` for an unknown ID:

```json
{ "error": "Invalid location ID: LOC999" }
```

## GET /api/traffic/analytics

| | |
| --- | --- |
| Method | GET |
| URL | `/api/traffic/analytics` |
| Purpose | Summarize the latest reading at each location |

Request: no body.

Response `200`:

```json
{
  "total_locations": 6,
  "total_vehicles": 2520,
  "average_speed": 29.8,
  "average_congestion": 65.5,
  "congested_locations": 3,
  "busiest_location": "Silk Board",
  "least_busy_location": "Whitefield",
  "highest_congestion_location": "Silk Board",
  "lowest_congestion_location": "Whitefield",
  "congested_definition": "HIGH or CRITICAL (congestion above 65%)",
  "data_source": "simulated",
  "storage_mode": "local-json"
}
```

The average congestion in the sample depends on rounding each location to one decimal place before the six values are averaged. The names and the total of 2520 vehicles come from the latest sample readings: 450, 630, 500, 210, 390, and 340.

An empty store returns zeros and `null` location names with status `200`.

## GET /api/traffic/prediction

| | |
| --- | --- |
| Method | GET |
| URL | `/api/traffic/prediction` |
| Purpose | Predict the next vehicle count with a moving average |

Optional query parameter: `location_id`.

Without a query parameter, response `200`:

```json
{
  "prediction_type": "Moving Average",
  "method": "Short-term prediction using a moving average of recent traffic observations.",
  "window_size": 5,
  "predictions": [
    {
      "location_id": "LOC001",
      "location": "MG Road",
      "current_vehicle_count": 450,
      "predicted_vehicle_count": 442,
      "prediction_type": "Moving Average",
      "window_size": 5,
      "recent_vehicle_counts": [400, 430, 450, 470, 460]
    }
  ]
}
```

The numbers inside `predictions` come from stored readings. The array above shows the documented calculation, not a promise that MG Road's stored series is exactly 400 through 460.

With `?location_id=LOC001`, the response is one prediction object rather than a list.

Response `404` when the location ID is unknown, or when that location has no readings.

Worked calculation:

```
(400 + 430 + 450 + 470 + 460) / 5 = 442
```

## POST /api/traffic/simulate

| | |
| --- | --- |
| Method | POST |
| URL | `/api/traffic/simulate` |
| Purpose | Append one new simulated reading for each location |

Request body: an empty JSON object, or no body.

```json
{}
```

Response `200`:

```json
{
  "message": "Simulated traffic update applied.",
  "data_source": "simulated",
  "storage_mode": "local-json",
  "updated_locations": 6,
  "locations": [
    {
      "location_id": "LOC001",
      "location_name": "MG Road",
      "vehicle_count": 468,
      "average_speed": 27,
      "road_capacity": 600,
      "congestion_percentage": 78.0,
      "congestion_status": "HIGH"
    }
  ]
}
```

Vehicle counts in the saved reading move by about -30 to +30 from the previous value and stay inside a realistic range. Speed changes by a few km/h. Congestion is recalculated from the new count and the unchanged road capacity.

Response `400` when the body is not a JSON object:

```json
{ "error": "Request body must be valid JSON." }
```

## GET /api/health

| | |
| --- | --- |
| Method | GET |
| URL | `/api/health` |
| Purpose | Check that the API can open its data store |

Response `200`:

```json
{
  "status": "ok",
  "storage_mode": "local-json",
  "data_source": "simulated",
  "record_count": 78
}
```

## Status codes

| Code | When it is used |
| --- | --- |
| 200 | The request succeeded |
| 400 | The request body or a field is invalid |
| 404 | The location ID is unknown or that location has no readings |
| 500 | Configuration is incomplete, or an unexpected error occurred |
| 503 | Cosmos DB could not be reached or a database operation failed |
