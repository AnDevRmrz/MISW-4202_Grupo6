from flask import Flask
import os
import json
from flask import Response
from datetime import datetime
import requests
import time
import uuid
import logging
import csv

app = Flask(__name__)
filename = './input.csv'
app.logger.setLevel(logging.INFO)
headers = ["id", "start", "end", "delta", "status"]


@app.get("/start")
def start():
    requests = int(os.environ.get("REQUESTS_TO_SEND", 5))
    interval = int(os.environ.get("INTERVAL", 0.5))
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
        "id": id,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "delta": delta,
        "status": res.ok
    }


def stress_test(requests, interval):
    results = {}

    for _ in range(requests):
        id = uuid.uuid4()
        app.logger.info(f"Sending request {id}")
        results[id] = send_request(id)
        time.sleep(interval)

    app.logger.info(f"Stress test completed with {requests} requests")
    print(results)
    write_csv(results)


def write_csv(results):
    with open(filename, "w") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for result in results.values():
            writer.writerow(result)