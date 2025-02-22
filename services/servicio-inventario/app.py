import csv
import datetime
import os
import random
from flask import Flask, jsonify

app = Flask(__name__)

app_context = app.app_context()
app_context.push()

filename = "./responses.csv"
headers = ["id", "start", "end", "delta", "status"]


@app.before_request
def init():
    global _is_initialized
    if not _is_initialized:
        try:
            if os.path.exists(filename):
                os.remove(filename)
            with open(filename, "w", encoding="UTF8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
        except Exception as e:
            app.logger.error(f"Error during initialization: {e}")
        finally:
            _is_initialized = True


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/product/<int:request_id>", methods=["GET"])
def get_product_inventory(request_id: int):
    """Retrieve inventory for a specific product."""
    start = datetime.now()
    random_number = random.randint(1, 100)

    if random_number <= 25:
        end = datetime.now()
        save_result(
            {
                "id": request_id,
                "start": start.isoformat(),
                "end": end.isoformat(),
                "delta": (end - start).microseconds,
                "status": False,
            }
        )

        return jsonify({"error": "Internal server error"}), 500

    response = {
        "name": "Producto de prueba",
        "product_id": "00112233",
        "inventory": 969,
    }

    end = datetime.now()
    save_result(
        {
            "id": request_id,
            "start": start.isoformat(),
            "end": end.isoformat(),
            "delta": (end - start).microseconds,
            "status": True,
        }
    )

    return jsonify(response), 200


def save_result(result):
    with open(filename, "a", encoding="UTF8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writerow(result)
