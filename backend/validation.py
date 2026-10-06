"""Input checks for traffic records and API requests."""

from datetime import datetime


def parse_timestamp(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("timestamp must be a valid ISO-8601 string")
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(text)
    except ValueError as exc:
        raise ValueError("timestamp must be a valid ISO-8601 string") from exc


def _require_number(record, field):
    value = record.get(field)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be a number")
    return value


def validate_traffic_record(record, known_location_ids=None):
    required = [
        "id",
        "location_id",
        "location_name",
        "timestamp",
        "vehicle_count",
        "average_speed",
        "road_capacity",
        "latitude",
        "longitude",
    ]
    if not isinstance(record, dict):
        raise ValueError("Traffic record must be an object")

    missing = [field for field in required if field not in record or record[field] in ("", None)]
    if missing:
        raise ValueError("Missing fields: " + ", ".join(missing))

    if known_location_ids is not None and record["location_id"] not in known_location_ids:
        raise ValueError(f"location_id must exist: {record['location_id']}")

    vehicle_count = _require_number(record, "vehicle_count")
    if vehicle_count < 0:
        raise ValueError("vehicle_count must be greater than or equal to 0")

    average_speed = _require_number(record, "average_speed")
    if average_speed < 0:
        raise ValueError("average_speed must be greater than or equal to 0")

    road_capacity = _require_number(record, "road_capacity")
    if road_capacity <= 0:
        raise ValueError("road_capacity must be greater than 0")

    parse_timestamp(record["timestamp"])
    return record
