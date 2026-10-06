"""Azure Functions HTTP API for the traffic dashboard.

Local URL: http://localhost:7071/api
Run with: func start
"""

import json
import logging

import azure.functions as func

from handlers import (
    handle_analytics,
    handle_get_location,
    handle_get_traffic,
    handle_health,
    handle_prediction,
    handle_simulate,
)
from repository import RepositoryError, get_repository

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}


def json_response(payload, status_code):
    return func.HttpResponse(
        body=json.dumps(payload),
        status_code=status_code,
        mimetype="application/json",
        headers=CORS_HEADERS,
    )


def dispatch(action):
    try:
        payload, status_code = action()
        return json_response(payload, status_code)
    except ValueError as exc:
        return json_response({"error": str(exc)}, 400)
    except RepositoryError as exc:
        logging.exception("Traffic data store error")
        return json_response({"error": str(exc)}, exc.status_code)
    except Exception:
        logging.exception("Unhandled traffic API error")
        return json_response({"error": "Unable to retrieve traffic data."}, 500)


@app.route(route="health", methods=["GET"])
def health(req: func.HttpRequest) -> func.HttpResponse:
    return dispatch(lambda: handle_health(get_repository()))


@app.route(route="traffic", methods=["GET"])
def get_traffic(req: func.HttpRequest) -> func.HttpResponse:
    return dispatch(lambda: handle_get_traffic(get_repository()))


@app.route(route="traffic/analytics", methods=["GET"])
def get_analytics(req: func.HttpRequest) -> func.HttpResponse:
    return dispatch(lambda: handle_analytics(get_repository()))


@app.route(route="traffic/prediction", methods=["GET"])
def get_prediction(req: func.HttpRequest) -> func.HttpResponse:
    location_id = req.params.get("location_id")
    return dispatch(lambda: handle_prediction(get_repository(), location_id))


@app.route(route="traffic/simulate", methods=["POST"])
def post_simulate(req: func.HttpRequest) -> func.HttpResponse:
    raw_body = req.get_body().decode("utf-8")
    return dispatch(lambda: handle_simulate(get_repository(), raw_body))


@app.route(route="traffic/{location_id}", methods=["GET"])
def get_traffic_by_location(req: func.HttpRequest) -> func.HttpResponse:
    location_id = req.route_params.get("location_id", "")
    return dispatch(lambda: handle_get_location(get_repository(), location_id))
