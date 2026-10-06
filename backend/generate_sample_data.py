"""Create the simulated academic dataset used by the dashboard.

The numbers are generated. They do not come from CCTV cameras or road sensors.
"""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from locations import DISCLAIMER, LOCATIONS

# Latest values are chosen so the demo shows LOW, MEDIUM, HIGH, and CRITICAL.
PROFILES = {
    "LOC001": {"start_vehicles": 280, "end_vehicles": 450, "start_speed": 38, "end_speed": 28},
    "LOC002": {"start_vehicles": 420, "end_vehicles": 630, "start_speed": 26, "end_speed": 18},
    "LOC003": {"start_vehicles": 300, "end_vehicles": 500, "start_speed": 34, "end_speed": 24},
    "LOC004": {"start_vehicles": 140, "end_vehicles": 210, "start_speed": 48, "end_speed": 42},
    "LOC005": {"start_vehicles": 250, "end_vehicles": 390, "start_speed": 40, "end_speed": 32},
    "LOC006": {"start_vehicles": 220, "end_vehicles": 340, "start_speed": 44, "end_speed": 35},
}

# Fixed variation so the sample file stays the same every time it is generated.
WIGGLE = [-12, 8, -5, 15, -8, 6, -10, 12, -4, 9, -6, 4, 0]


def _lerp(start, end, ratio):
    return start + (end - start) * ratio


def build_records():
    start = datetime(2026, 10, 6, 4, 0, tzinfo=timezone.utc)
    slots = len(WIGGLE)
    records = []
    for index in range(slots):
        moment = start + timedelta(minutes=30 * index)
        stamp = moment.strftime("%Y-%m-%dT%H:%M:%SZ")
        ratio = index / (slots - 1)
        for location in LOCATIONS:
            profile = PROFILES[location["location_id"]]
            if index == slots - 1:
                vehicles = profile["end_vehicles"]
                speed = profile["end_speed"]
            else:
                vehicles = round(
                    _lerp(profile["start_vehicles"], profile["end_vehicles"], ratio) + WIGGLE[index]
                )
                speed = round(_lerp(profile["start_speed"], profile["end_speed"], ratio))
            records.append(
                {
                    "id": f"traffic-{location['location_id']}-{stamp.replace('-', '').replace(':', '')}",
                    "location_id": location["location_id"],
                    "location_name": location["location_name"],
                    "timestamp": stamp,
                    "vehicle_count": max(20, int(vehicles)),
                    "average_speed": max(8, int(speed)),
                    "road_capacity": location["road_capacity"],
                    "latitude": location["latitude"],
                    "longitude": location["longitude"],
                }
            )
    return records


def main():
    payload = {
        "disclaimer": DISCLAIMER,
        "description": (
            "Simulated academic traffic observations for six Bengaluru locations. "
            "These records are not from CCTV, IoT sensors, or a live traffic API."
        ),
        "generated_for": "Smart Traffic Monitoring and Analytics Dashboard",
        "records": build_records(),
    }
    destination = Path(__file__).resolve().parent.parent / "data" / "sample_traffic_data.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(payload['records'])} records to {destination}")


if __name__ == "__main__":
    main()
