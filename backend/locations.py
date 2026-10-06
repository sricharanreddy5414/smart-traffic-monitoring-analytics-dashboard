"""Bengaluru locations used by this academic traffic prototype."""

LOCATIONS = [
    {
        "location_id": "LOC001",
        "location_name": "MG Road",
        "road_capacity": 600,
        "latitude": 12.9756,
        "longitude": 77.6065,
    },
    {
        "location_id": "LOC002",
        "location_name": "Silk Board",
        "road_capacity": 720,
        "latitude": 12.9177,
        "longitude": 77.6233,
    },
    {
        "location_id": "LOC003",
        "location_name": "Electronic City",
        "road_capacity": 640,
        "latitude": 12.8456,
        "longitude": 77.6603,
    },
    {
        "location_id": "LOC004",
        "location_name": "Whitefield",
        "road_capacity": 560,
        "latitude": 12.9698,
        "longitude": 77.7499,
    },
    {
        "location_id": "LOC005",
        "location_name": "Marathahalli",
        "road_capacity": 600,
        "latitude": 12.9591,
        "longitude": 77.6974,
    },
    {
        "location_id": "LOC006",
        "location_name": "Hebbal",
        "road_capacity": 680,
        "latitude": 13.0358,
        "longitude": 77.5970,
    },
]

LOCATION_BY_ID = {item["location_id"]: item for item in LOCATIONS}

# Shown by the API and the dashboard. This prototype does not read CCTV or sensors.
DISCLAIMER = (
    "Traffic data is simulated for academic demonstration. "
    "The architecture can later be connected to IoT sensors, "
    "CCTV/computer vision systems, GPS feeds, or external traffic APIs."
)
