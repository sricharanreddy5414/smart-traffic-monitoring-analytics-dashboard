"""Congestion calculation for the traffic dashboard.

The percentage is not stored in the database. Every API response calculates it:

    congestion_percentage = (vehicle_count / road_capacity) * 100

Classification:
    0–40   LOW
    41–65  MEDIUM
    66–85  HIGH
    86+    CRITICAL
"""


def congestion_percentage(vehicle_count, road_capacity):
    if road_capacity <= 0:
        raise ValueError("road_capacity must be greater than 0")
    if vehicle_count < 0:
        raise ValueError("vehicle_count must be greater than or equal to 0")
    return round((vehicle_count / road_capacity) * 100, 1)


def congestion_status(percentage):
    if percentage <= 40:
        return "LOW"
    if percentage <= 65:
        return "MEDIUM"
    if percentage <= 85:
        return "HIGH"
    return "CRITICAL"


def is_congested(percentage):
    """HIGH and CRITICAL locations count as congested (above 65%)."""
    return percentage > 65


def with_congestion(record):
    percentage = congestion_percentage(record["vehicle_count"], record["road_capacity"])
    enriched = dict(record)
    enriched["congestion_percentage"] = percentage
    enriched["congestion_status"] = congestion_status(percentage)
    return enriched
