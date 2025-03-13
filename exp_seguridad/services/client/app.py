from faker import Faker
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
import hashlib
import hmac
import random

fake = Faker()

app = Flask(__name__)
filename = './input.csv'
app.logger.setLevel(logging.INFO)
headers = ["id", "data", "start", "end", "delta", "valid_content", "status"]

SECRET_KEY = os.getenv("SECRET_KEY", "mykeyishiddensomewhereinthecloud")

def generate_hmac(data: dict) -> str:
    json_data = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
    return hmac.new(SECRET_KEY.encode(), json_data.encode(), hashlib.sha256).hexdigest()


@app.get("/start")
def start():
    requests = int(os.environ.get("REQUESTS_TO_SEND", 20))
    interval = float(os.environ.get("INTERVAL", 0.5))
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


def send_request(id, valid_content):
    start = datetime.now()
    data_to_send = {}
    payload = {
        "quantity": random.randint(1, 10),
        "description": fake.sentence(),
        "date": fake.date()
    }
    data_to_send["payload"] = payload
    if valid_content:
        hmac_to_send = generate_hmac(payload)
        data_to_send["hash"] = hmac_to_send
    else:
        data_to_send["hash"] = fake.lexify(text='?'*64)

    res = requests.put(f"http://api_gateway/inventory/product/{id}", data=data_to_send)
    end = datetime.now()
    delta = (end - start).microseconds
    return {
        "id": id,
        "data": data_to_send,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "delta": delta,
        "valid_content": valid_content,
        "status": res.ok
    }


def stress_test(requests, interval):
    results = {}

    for _ in range(requests):
        id = uuid.uuid4()
        valid_content = random.randint(1, 10) <= 8
        app.logger.info(f"Sending request {id}")
        results[id] = send_request(id, valid_content)
        time.sleep(interval)

    app.logger.info(f"Stress test completed with {requests} requests")
    write_csv(results)


def write_csv(results):
    with open(filename, "w") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for result in results.values():
            writer.writerow(result)