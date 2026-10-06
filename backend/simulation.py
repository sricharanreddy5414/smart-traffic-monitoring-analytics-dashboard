"""Controlled traffic simulation for classroom demonstration.

There are no live sensors in this project. Each click creates one new reading
per location. Vehicle count changes by about -30 to +30, and speed changes by
a few km/h. Values stay inside a realistic range.
"""

import random
from datetime import datetime, timedelta, timezone

from locations import LOCATION_BY_ID


def _parse(timestamp):
    text = timestamp[:-1] + "+00:00" if timestamp.endswith("Z") else timestamp
    return datetime.fromisoformat(text)


def _format(value):
    return value.astimezone(timezone.utc).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")


def next_timestamp(records):
    now = datetime.now(timezone.utc).replace(microsecond=0)
    if not records:
        return _format(now)
    latest = max(_parse(record["timestamp"]) for record in records)
    if now <= latest:
        return _format(latest + timedelta(minutes=5))
    return _format(now)


def simulate_updates(records, rng=None):
    rng = rng or random
    stamp = next_timestamp(records)
    stamp_token = stamp.replace("-", "").replace(":", "")
    latest = {}
    for record in records:
        current = latest.get(record["location_id"])
        if current is None or record["timestamp"] > current["timestamp"]:
            latest[record["location_id"]] = record

    created = []
    for location_id, meta in LOCATION_BY_ID.items():
        current = latest.get(location_id)
        if current is None:
            base_count = max(40, int(meta["road_capacity"] * 0.45))
            base_speed = 35
            capacity = meta["road_capacity"]
            name = meta["location_name"]
            latitude = meta["latitude"]
            longitude = meta["longitude"]
        else:
            base_count = int(current["vehicle_count"])
            base_speed = int(current["average_speed"])
            capacity = int(current["road_capacity"])
            name = current["location_name"]
            latitude = current["latitude"]
            longitude = current["longitude"]

        delta_vehicles = rng.randint(-30, 30)
        vehicle_count = base_count + delta_vehicles
        vehicle_count = max(20, min(capacity + 80, vehicle_count))

        speed_delta = rng.randint(-3, 3)
        if delta_vehicles > 10:
            speed_delta -= 1
        elif delta_vehicles < -10:
            speed_delta += 1
        average_speed = max(8, min(65, base_speed + speed_delta))

        created.append(
            {
                "id": f"traffic-{location_id}-{stamp_token}",
                "location_id": location_id,
                "location_name": name,
                "timestamp": stamp,
                "vehicle_count": int(vehicle_count),
                "average_speed": int(average_speed),
                "road_capacity": int(capacity),
                "latitude": latitude,
                "longitude": longitude,
            }
        )
    return created
