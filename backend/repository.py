"""Traffic storage.

Cosmos DB is used when COSMOS_ENDPOINT and COSMOS_KEY are set.
If they are empty, the API uses a local JSON file so the project can be
demonstrated before Azure credentials are configured. That local file is a
real store for development. It is not a pretend Cosmos connection.
"""

import json
import os
import threading
from pathlib import Path

from locations import LOCATION_BY_ID
from validation import validate_traffic_record

BACKEND_DIR = Path(__file__).resolve().parent
REPO_ROOT = BACKEND_DIR.parent
LOCAL_STORE = BACKEND_DIR / ".local_data" / "traffic_store.json"


class RepositoryError(Exception):
    def __init__(self, message, status_code=500):
        super().__init__(message)
        self.status_code = status_code


def env_value(name):
    value = os.environ.get(name, "")
    if not isinstance(value, str):
        return None
    value = value.strip()
    return value or None


def sample_data_path():
    """Find the sample file in the repo layout or inside a deployed Function App."""
    candidates = [
        BACKEND_DIR / "data" / "sample_traffic_data.json",
        REPO_ROOT / "data" / "sample_traffic_data.json",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise RepositoryError("Sample traffic data file was not found.", 500)


def load_sample_records():
    with sample_data_path().open(encoding="utf-8") as handle:
        payload = json.load(handle)
    records = payload["records"] if isinstance(payload, dict) else payload
    if not isinstance(records, list):
        raise RepositoryError("Sample traffic data is not a list of records.", 500)
    known_ids = set(LOCATION_BY_ID)
    for record in records:
        validate_traffic_record(record, known_location_ids=known_ids)
    return records


def public_record(record):
    """Hide Cosmos system fields such as _etag and _rid."""
    return {key: value for key, value in record.items() if not str(key).startswith("_")}


class LocalJsonRepository:
    """File store used when Cosmos DB environment variables are not set."""

    def __init__(self, store_path=None):
        self.store_path = Path(store_path) if store_path else LOCAL_STORE
        self._lock = threading.Lock()
        self.mode = "local-json"
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.store_path.exists():
            records = load_sample_records()
            self.store_path.write_text(json.dumps(records, indent=2), encoding="utf-8")

    def get_all(self):
        with self._lock:
            return json.loads(self.store_path.read_text(encoding="utf-8"))

    def add_records(self, records):
        known_ids = set(LOCATION_BY_ID)
        for record in records:
            validate_traffic_record(record, known_location_ids=known_ids)
        with self._lock:
            current = json.loads(self.store_path.read_text(encoding="utf-8"))
            current.extend(records)
            self.store_path.write_text(json.dumps(current, indent=2), encoding="utf-8")
        return records


class CosmosRepository:
    """Azure Cosmos DB store. Credentials come only from environment variables."""

    def __init__(self):
        endpoint = env_value("COSMOS_ENDPOINT")
        key = env_value("COSMOS_KEY")
        database_name = env_value("COSMOS_DATABASE") or "TrafficDB"
        container_name = env_value("COSMOS_CONTAINER") or "TrafficData"
        if not endpoint or not key:
            missing = []
            if not endpoint:
                missing.append("COSMOS_ENDPOINT")
            if not key:
                missing.append("COSMOS_KEY")
            raise RepositoryError(
                "Cosmos DB configuration is incomplete. Set " + ", ".join(missing) + ".",
                500,
            )
        try:
            from azure.cosmos import CosmosClient, PartitionKey
        except ImportError as exc:
            raise RepositoryError(
                "The azure-cosmos package is not installed. Run pip install -r requirements.txt.",
                500,
            ) from exc

        try:
            client = CosmosClient(endpoint, credential=key)
        except Exception as exc:
            raise RepositoryError(
                "Unable to connect to Azure Cosmos DB. Check the endpoint and key.",
                503,
            ) from exc

        try:
            database = client.create_database_if_not_exists(id=database_name)
            container = database.create_container_if_not_exists(
                id=container_name,
                partition_key=PartitionKey(path="/location_id"),
            )
        except Exception:
            # Use a database and container the student already created in the Azure portal.
            try:
                database = client.get_database_client(database_name)
                container = database.get_container_client(container_name)
                list(container.query_items(
                    query="SELECT TOP 1 c.id FROM c",
                    enable_cross_partition_query=True,
                ))
            except Exception as exc:
                raise RepositoryError(
                    "Unable to connect to Azure Cosmos DB. Check the endpoint, key, database, and container.",
                    503,
                ) from exc

        self._container = container
        self.mode = "cosmos-db"
        self._seed_if_empty()

    def _seed_if_empty(self):
        existing = list(self._container.query_items(
            query="SELECT TOP 1 c.id FROM c",
            enable_cross_partition_query=True,
        ))
        if existing:
            return
        for record in load_sample_records():
            self._container.upsert_item(record)

    def get_all(self):
        try:
            return list(self._container.read_all_items())
        except Exception as exc:
            raise RepositoryError("Unable to read traffic data from Cosmos DB.", 503) from exc

    def add_records(self, records):
        known_ids = set(LOCATION_BY_ID)
        saved = []
        try:
            for record in records:
                validate_traffic_record(record, known_location_ids=known_ids)
                self._container.upsert_item(dict(record))
                saved.append(record)
        except RepositoryError:
            raise
        except ValueError:
            raise
        except Exception as exc:
            raise RepositoryError("Unable to save traffic data to Cosmos DB.", 503) from exc
        return saved


_repository = None
_repository_lock = threading.Lock()


def get_repository():
    global _repository
    with _repository_lock:
        if _repository is None:
            endpoint = env_value("COSMOS_ENDPOINT")
            key = env_value("COSMOS_KEY")
            if endpoint or key:
                _repository = CosmosRepository()
            else:
                _repository = LocalJsonRepository()
        return _repository


def reset_repository():
    """Used by tests so a previous connection is not reused."""
    global _repository
    with _repository_lock:
        _repository = None
