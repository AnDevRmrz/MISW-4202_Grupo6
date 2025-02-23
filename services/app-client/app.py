from flask import Flask
import os
import json
from flask import Response
from datetime import datetime
import requests
import time
import uuid
import logging

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

@app.get("/start")
def start():
    requests = int(os.environ.get("REQUESTS_TO_SEND", 300))
    interval = float(os.environ.get("INTERVAL", 0.1))
    data = {
        "message": "Starting Stress Test",
        "requests": requests,
        "interval": interval
    }
    response = Response(json.dumps(data), 200)

    @response.call_on_close
    def on_close():
        stress_test(requests, interval)

    return response


def send_request(id):
    start = datetime.now()
    res = requests.get(f"http://api_gateway/inventory/product/{id}")
    end = datetime.now()
    delta = (end - start).microseconds
    return {
        "type": "request",
        "id": id,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "delta": delta,
        "status": res.ok
    }

def stress_test(requests, interval):
    for _ in range(requests):
        id = str(uuid.uuid4())
        app.logger.info(f"Sending request {id}")
        result = send_request(id)
        save_result(result)
        time.sleep(interval)

    app.logger.info(f"Stress test completed with {requests} requests")


def save_result(result):
    try:
        requests.post("http://db_service:5000/insert", json=result)
    except Exception as e:
        app.logger.error(f"Error sending to database: {e}")