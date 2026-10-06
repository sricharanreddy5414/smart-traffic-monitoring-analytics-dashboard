import json
import os
import random
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from analytics import build_analytics
from congestion import congestion_percentage, congestion_status, is_congested
from generate_sample_data import build_records
from handlers import (
    handle_analytics,
    handle_get_location,
    handle_get_traffic,
    handle_prediction,
    handle_simulate,
)
from prediction import moving_average_prediction
from repository import (
    LocalJsonRepository,
    RepositoryError,
    get_repository,
    public_record,
    reset_repository,
)
from simulation import simulate_updates
from validation import validate_traffic_record


class MemoryRepository:
    def __init__(self, records):
        self.records = [dict(item) for item in records]
        self.mode = "memory"

    def get_all(self):
        return [dict(item) for item in self.records]

    def add_records(self, records):
        self.records.extend(records)
        return records


class CongestionTests(unittest.TestCase):
    def test_problem_statement_example(self):
        self.assertEqual(congestion_percentage(450, 600), 75.0)
        self.assertEqual(congestion_status(75), "HIGH")

    def test_status_boundaries(self):
        self.assertEqual(congestion_status(0), "LOW")
        self.assertEqual(congestion_status(40), "LOW")
        self.assertEqual(congestion_status(41), "MEDIUM")
        self.assertEqual(congestion_status(65), "MEDIUM")
        self.assertEqual(congestion_status(66), "HIGH")
        self.assertEqual(congestion_status(85), "HIGH")
        self.assertEqual(congestion_status(86), "CRITICAL")
        self.assertFalse(is_congested(65))
        self.assertTrue(is_congested(66))

    def test_invalid_capacity(self):
        with self.assertRaises(ValueError):
            congestion_percentage(10, 0)


class AnalyticsAndPredictionTests(unittest.TestCase):
    def test_sample_analytics(self):
        analytics = build_analytics(build_records())
        self.assertEqual(analytics["total_locations"], 6)
        self.assertEqual(analytics["total_vehicles"], 2520)
        self.assertEqual(analytics["average_speed"], 29.8)
        self.assertEqual(analytics["congested_locations"], 3)
        self.assertEqual(analytics["busiest_location"], "Silk Board")
        self.assertEqual(analytics["least_busy_location"], "Whitefield")
        self.assertEqual(analytics["highest_congestion_location"], "Silk Board")
        self.assertEqual(analytics["lowest_congestion_location"], "Whitefield")
        self.assertGreater(analytics["average_congestion"], 0)

    def test_empty_analytics(self):
        analytics = build_analytics([])
        self.assertEqual(analytics["total_vehicles"], 0)
        self.assertIsNone(analytics["busiest_location"])

    def test_moving_average_example(self):
        counts = [400, 430, 450, 470, 460]
        records = []
        for index, count in enumerate(counts):
            records.append(
                {
                    "id": f"sample-{index}",
                    "location_id": "LOC001",
                    "location_name": "MG Road",
                    "timestamp": f"2026-10-06T{index:02d}:00:00Z",
                    "vehicle_count": count,
                    "average_speed": 30,
                    "road_capacity": 600,
                    "latitude": 12.97,
                    "longitude": 77.60,
                }
            )
        prediction = moving_average_prediction(records, "LOC001")
        self.assertEqual(prediction["current_vehicle_count"], 460)
        self.assertEqual(prediction["predicted_vehicle_count"], 442)
        self.assertEqual(prediction["prediction_type"], "Moving Average")
        self.assertEqual(prediction["recent_vehicle_counts"], counts)

    def test_sample_prediction_matches_recent_average(self):
        prediction = moving_average_prediction(build_records(), "LOC001")
        counts = prediction["recent_vehicle_counts"]
        self.assertEqual(prediction["current_vehicle_count"], 450)
        self.assertEqual(prediction["predicted_vehicle_count"], round(sum(counts) / len(counts)))


class SimulationTests(unittest.TestCase):
    def test_simulation_changes_vehicle_count_within_limits(self):
        records = build_records()

        class FixedRng:
            def randint(self, start, end):
                if start == -30:
                    return 30
                return 1

        created = simulate_updates(records, rng=FixedRng())
        self.assertEqual(len(created), 6)
        by_id = {item["location_id"]: item for item in created}
        self.assertEqual(by_id["LOC001"]["vehicle_count"], 480)
        self.assertGreaterEqual(by_id["LOC004"]["average_speed"], 8)
        for item in created:
            self.assertGreaterEqual(item["vehicle_count"], 20)
            self.assertLessEqual(item["vehicle_count"], item["road_capacity"] + 80)
            self.assertGreaterEqual(item["average_speed"], 8)
            self.assertLessEqual(item["average_speed"], 65)


class HandlerTests(unittest.TestCase):
    def setUp(self):
        self.repository = MemoryRepository(build_records())

    def test_traffic_payload(self):
        payload, status = handle_get_traffic(self.repository)
        self.assertEqual(status, 200)
        self.assertEqual(len(payload["locations"]), 6)
        mg_road = next(item for item in payload["locations"] if item["location_name"] == "MG Road")
        self.assertEqual(mg_road["congestion_percentage"], 75.0)
        self.assertEqual(mg_road["congestion_status"], "HIGH")
        self.assertIn("simulated", payload["disclaimer"])

    def test_location_and_invalid_location(self):
        payload, status = handle_get_location(self.repository, "LOC002")
        self.assertEqual(status, 200)
        self.assertEqual(payload["location"]["location_name"], "Silk Board")
        self.assertEqual(payload["location"]["congestion_status"], "CRITICAL")

        error, error_status = handle_get_location(self.repository, "LOC999")
        self.assertEqual(error_status, 404)
        self.assertIn("Invalid location ID", error["error"])

    def test_analytics_and_prediction_endpoints(self):
        analytics, status = handle_analytics(self.repository)
        self.assertEqual(status, 200)
        self.assertEqual(analytics["total_locations"], 6)

        all_predictions, prediction_status = handle_prediction(self.repository)
        self.assertEqual(prediction_status, 200)
        self.assertEqual(all_predictions["prediction_type"], "Moving Average")
        self.assertEqual(len(all_predictions["predictions"]), 6)

        one, one_status = handle_prediction(self.repository, "LOC001")
        self.assertEqual(one_status, 200)
        self.assertEqual(one["location"], "MG Road")

    def test_simulate_endpoint_saves_new_readings(self):
        before = len(self.repository.get_all())
        payload, status = handle_simulate(self.repository, "{}", rng=random.Random(3))
        self.assertEqual(status, 200)
        self.assertEqual(payload["updated_locations"], 6)
        self.assertEqual(len(self.repository.get_all()), before + 6)
        refreshed, _ = handle_get_traffic(self.repository)
        self.assertEqual(refreshed["last_updated"], payload["locations"][0]["timestamp"])

    def test_invalid_simulate_body(self):
        with self.assertRaises(ValueError):
            handle_simulate(self.repository, "not-json")

    def test_empty_database(self):
        empty = MemoryRepository([])
        payload, status = handle_get_traffic(empty)
        self.assertEqual(status, 200)
        self.assertEqual(payload["locations"], [])
        analytics, _ = handle_analytics(empty)
        self.assertEqual(analytics["total_locations"], 0)


class ValidationAndStoreTests(unittest.TestCase):
    def test_validation_rules(self):
        record = dict(build_records()[0])
        validate_traffic_record(record, known_location_ids={"LOC001"})
        record["vehicle_count"] = -1
        with self.assertRaises(ValueError):
            validate_traffic_record(record)
        record["vehicle_count"] = 10
        record["road_capacity"] = 0
        with self.assertRaises(ValueError):
            validate_traffic_record(record)
        record["road_capacity"] = 100
        record["timestamp"] = "not-a-time"
        with self.assertRaises(ValueError):
            validate_traffic_record(record)
        record["timestamp"] = "2026-10-06T10:00:00Z"
        record["location_id"] = "NOPE"
        with self.assertRaises(ValueError):
            validate_traffic_record(record, known_location_ids={"LOC001"})

    def test_local_json_repository_persists(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repository = LocalJsonRepository(Path(temp_dir) / "traffic_store.json")
            before = len(repository.get_all())
            self.assertGreater(before, 0)
            created = simulate_updates(repository.get_all(), rng=random.Random(1))
            repository.add_records(created)
            reloaded = LocalJsonRepository(Path(temp_dir) / "traffic_store.json")
            self.assertEqual(len(reloaded.get_all()), before + 6)

    def test_cosmos_fields_are_hidden(self):
        cleaned = public_record({"id": "traffic-001", "location_id": "LOC001", "_etag": "abc"})
        self.assertNotIn("_etag", cleaned)
        self.assertEqual(cleaned["id"], "traffic-001")

    def test_partial_cosmos_configuration_fails_clearly(self):
        previous_endpoint = os.environ.get("COSMOS_ENDPOINT")
        previous_key = os.environ.get("COSMOS_KEY")
        os.environ["COSMOS_ENDPOINT"] = "https://example.documents.azure.com:443/"
        os.environ.pop("COSMOS_KEY", None)
        reset_repository()
        try:
            with self.assertRaises(RepositoryError):
                get_repository()
        finally:
            if previous_endpoint is None:
                os.environ.pop("COSMOS_ENDPOINT", None)
            else:
                os.environ["COSMOS_ENDPOINT"] = previous_endpoint
            if previous_key is None:
                os.environ.pop("COSMOS_KEY", None)
            else:
                os.environ["COSMOS_KEY"] = previous_key
            reset_repository()

    def test_sample_file_matches_generator(self):
        sample_path = Path(__file__).resolve().parents[2] / "data" / "sample_traffic_data.json"
        payload = json.loads(sample_path.read_text(encoding="utf-8"))
        self.assertEqual(payload["records"], build_records())
        self.assertIn("simulated", payload["disclaimer"].lower())


if __name__ == "__main__":
    unittest.main()
