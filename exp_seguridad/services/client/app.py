from faker import Faker
from flask import Flask, Response
import os
import json
import requests
import time
import uuid
import logging
import csv
import hashlib
import hmac
import random
import urllib.parse
from datetime import datetime

fake = Faker()

app = Flask(__name__)
filename = './input.csv'
app.logger.setLevel(logging.INFO)
headers = ["id", "start", "end", "delta", "valid_content", "status"]

SECRET_KEY = os.getenv("SECRET_KEY", "mykeyishiddensomewhereinthecloud")

def generate_hmac(data: dict) -> str:
    json_data = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
    return hmac.new(SECRET_KEY.encode(), json_data.encode(), hashlib.sha256).hexdigest()


@app.route("/start")
def start():
    requests_count = int(os.environ.get("REQUESTS_TO_SEND", 20))
    interval = float(os.environ.get("INTERVAL", 0.5))
    data = {
        "message": "Starting Stress Test",
        "requests": requests_count,
        "interval": interval
    }
    response = Response(json.dumps(data), 200)

    @response.call_on_close
    def on_close():
        stress_test(requests_count, interval)

    return response


def send_request(id, valid_content):
    start = datetime.now()
    
    # Generate random payload
    payload = {
        "quantity": random.randint(1, 10),
        "description": fake.sentence(),
        "date": fake.date()
    }
    
    # Generate HMAC
    if valid_content:
        hmac_to_send = generate_hmac(payload)
    else:
        hmac_to_send = fake.lexify(text='?'*64)
    
    # URL encode the payload
    encoded_payload = urllib.parse.quote(json.dumps(payload))
    
    # Build the URL with query parameters
    request_url = f"http://api_gateway/inventory/product/{id}?payload={encoded_payload}&hash={hmac_to_send}"
    
    app.logger.info(f"Sending request to: {request_url}")
    
    # Send request
    res = requests.get(request_url)
    
    end = datetime.now()
    delta = (end - start).microseconds
    
    return {
        "id": id,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "delta": delta,
        "valid_content": valid_content,
        "status": res.ok
    }


def stress_test(requests_count, interval):
    results = {}

    for _ in range(requests_count):
        id = uuid.uuid4()
        valid_content = random.randint(1, 10) <= 8  # 80% chance of valid content
        app.logger.info(f"Sending request {id} with valid content: {valid_content}")
        results[id] = send_request(id, valid_content)
        time.sleep(interval)

    app.logger.info(f"Stress test completed with {requests_count} requests")
    write_csv(results)


def write_csv(results):
    with open(filename, "w") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for result in results.values():
            writer.writerow(result)


@app.route("/health", methods=["GET"])
def health_check():
    return json.dumps({"status": "healthy", "service": "client"}), 200, {'Content-Type': 'application/json'}


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)