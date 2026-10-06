"""HTTP API behaviour, independent of the Azure Functions runtime.

function_app.py calls these handlers and converts the result to JSON.
"""

import json

from analytics import build_analytics, latest_by_location
from congestion import with_congestion
from locations import DISCLAIMER, LOCATION_BY_ID
from prediction import moving_average_prediction, predict_all
from repository import public_record
from simulation import simulate_updates

RESERVED_PATHS = {"analytics", "prediction", "simulate", "health"}


def _clean_records(repository):
    return [public_record(item) for item in repository.get_all()]


def _meta(repository):
    return {
        "data_source": "simulated",
        "disclaimer": DISCLAIMER,
        "storage_mode": repository.mode,
    }


def handle_health(repository):
    records = _clean_records(repository)
    return {
        "status": "ok",
        "storage_mode": repository.mode,
        "data_source": "simulated",
        "record_count": len(records),
    }, 200


def handle_get_traffic(repository):
    records = _clean_records(repository)
    if not records:
        payload = _meta(repository)
        payload.update({"last_updated": None, "locations": [], "history": []})
        return payload, 200

    history = sorted(
        (with_congestion(record) for record in records),
        key=lambda item: (item["timestamp"], item["location_id"]),
    )
    latest = sorted(
        (with_congestion(record) for record in latest_by_location(records)),
        key=lambda item: item["location_id"],
    )
    payload = _meta(repository)
    payload.update(
        {
            "last_updated": max(item["timestamp"] for item in latest),
            "locations": latest,
            "history": history,
        }
    )
    return payload, 200


def handle_get_location(repository, location_id):
    if location_id in RESERVED_PATHS:
        raise ValueError("Use the dedicated endpoint for this resource.")
    if location_id not in LOCATION_BY_ID:
        return {"error": f"Invalid location ID: {location_id}"}, 404

    matches = [
        with_congestion(record)
        for record in _clean_records(repository)
        if record["location_id"] == location_id
    ]
    matches.sort(key=lambda item: item["timestamp"])
    if not matches:
        return {"error": f"No traffic data available for {location_id}."}, 404

    payload = _meta(repository)
    payload.update({"location": matches[-1], "history": matches})
    return payload, 200


def handle_analytics(repository):
    payload = build_analytics(_clean_records(repository))
    payload.update(_meta(repository))
    return payload, 200


def handle_prediction(repository, location_id=None):
    records = _clean_records(repository)
    if location_id:
        if location_id not in LOCATION_BY_ID:
            return {"error": f"Invalid location ID: {location_id}"}, 404
        prediction = moving_average_prediction(records, location_id)
        if prediction is None:
            return {"error": "No traffic data available."}, 404
        prediction.update(_meta(repository))
        prediction["method"] = (
            "Short-term prediction using a moving average of recent traffic observations."
        )
        return prediction, 200

    predictions = predict_all(records, list(LOCATION_BY_ID))
    payload = _meta(repository)
    payload.update(
        {
            "prediction_type": "Moving Average",
            "method": (
                "Short-term prediction using a moving average of recent traffic observations."
            ),
            "window_size": 5,
            "predictions": predictions,
        }
    )
    return payload, 200


def handle_simulate(repository, raw_body="", rng=None):
    if raw_body and raw_body.strip():
        try:
            parsed = json.loads(raw_body)
        except json.JSONDecodeError as exc:
            raise ValueError("Request body must be valid JSON.") from exc
        if not isinstance(parsed, dict):
            raise ValueError("Request body must be a JSON object.")

    created = simulate_updates(_clean_records(repository), rng=rng)
    repository.add_records(created)
    enriched = [with_congestion(item) for item in created]
    payload = _meta(repository)
    payload.update(
        {
            "message": "Simulated traffic update applied.",
            "updated_locations": len(enriched),
            "locations": enriched,
        }
    )
    return payload, 200
