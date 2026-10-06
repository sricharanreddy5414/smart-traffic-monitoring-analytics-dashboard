"""Short-term traffic prediction using a simple moving average.

This is a basic academic method. It is not a machine learning model.

Example:
    recent vehicle counts = 400, 430, 450, 470, 460
    moving average = (400 + 430 + 450 + 470 + 460) / 5 = 442
    predicted vehicle count = 442
"""

WINDOW_SIZE = 5


def moving_average_prediction(records, location_id):
    series = sorted(
        [record for record in records if record["location_id"] == location_id],
        key=lambda record: record["timestamp"],
    )
    if not series:
        return None

    recent = series[-WINDOW_SIZE:]
    counts = [int(item["vehicle_count"]) for item in recent]
    predicted = round(sum(counts) / len(counts))
    current = series[-1]
    return {
        "location_id": location_id,
        "location": current["location_name"],
        "current_vehicle_count": int(current["vehicle_count"]),
        "predicted_vehicle_count": predicted,
        "prediction_type": "Moving Average",
        "window_size": len(counts),
        "recent_vehicle_counts": counts,
    }


def predict_all(records, location_ids):
    predictions = []
    for location_id in location_ids:
        item = moving_average_prediction(records, location_id)
        if item is not None:
            predictions.append(item)
    return predictions
