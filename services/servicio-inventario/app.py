from datetime import datetime
import random
import requests
from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/product/<request_id>", methods=["GET"])
def get_product_inventory(request_id: str):
    """Retrieve inventory for a specific product."""
    start = datetime.now()
    random_number = random.randint(1, 100)

    if random_number <= 25:
        end = datetime.now()
        save_result({
            "type": "response",
            "request_id": request_id,
            "start": start.isoformat(),
            "end": end.isoformat(),
            "delta": (end - start).microseconds,
            "status": False,
        })
        return jsonify({"error": "Internal server error"}), 500

    response = {
        "name": "Producto de prueba",
        "product_id": "00112233",
        "inventory": 969,
    }

    end = datetime.now()
    save_result({
        "type": "response",
        "request_id": request_id,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "delta": (end - start).microseconds,
        "status": True,
    })

    return jsonify(response), 200

def save_result(result):
    try:
        requests.post("http://db_service:5000/insert", json=result)
    except Exception as e:
        app.logger.error(f"Error sending to database: {e}")
