"""Summary analytics calculated from the latest reading at each location."""

from congestion import is_congested, with_congestion


def latest_by_location(records):
    """Keep the newest record for each location. ISO-8601 UTC timestamps sort correctly."""
    latest = {}
    for record in records:
        current = latest.get(record["location_id"])
        if current is None or record["timestamp"] > current["timestamp"]:
            latest[record["location_id"]] = record
    return list(latest.values())


def build_analytics(records):
    latest = [with_congestion(record) for record in latest_by_location(records)]
    empty = {
        "total_locations": 0,
        "total_vehicles": 0,
        "average_speed": 0,
        "average_congestion": 0,
        "congested_locations": 0,
        "busiest_location": None,
        "least_busy_location": None,
        "highest_congestion_location": None,
        "lowest_congestion_location": None,
        "congested_definition": "HIGH or CRITICAL (congestion above 65%)",
    }
    if not latest:
        return empty

    total_vehicles = int(sum(item["vehicle_count"] for item in latest))
    average_speed = round(sum(item["average_speed"] for item in latest) / len(latest), 1)
    average_congestion = round(
        sum(item["congestion_percentage"] for item in latest) / len(latest),
        1,
    )
    congested = [item for item in latest if is_congested(item["congestion_percentage"])]
    busiest = max(latest, key=lambda item: (item["vehicle_count"], item["location_name"]))
    least_busy = min(latest, key=lambda item: (item["vehicle_count"], item["location_name"]))
    highest = max(latest, key=lambda item: (item["congestion_percentage"], item["location_name"]))
    lowest = min(latest, key=lambda item: (item["congestion_percentage"], item["location_name"]))

    return {
        "total_locations": len(latest),
        "total_vehicles": total_vehicles,
        "average_speed": average_speed,
        "average_congestion": average_congestion,
        "congested_locations": len(congested),
        "busiest_location": busiest["location_name"],
        "least_busy_location": least_busy["location_name"],
        "highest_congestion_location": highest["location_name"],
        "lowest_congestion_location": lowest["location_name"],
        "congested_definition": "HIGH or CRITICAL (congestion above 65%)",
    }
