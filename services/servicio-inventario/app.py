from datetime import datetime
import glob
import os
import random
import socket
from flask import Flask, jsonify
from models import db, Response

app = Flask(__name__)

# Configure SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///responses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)

# Create tables within application context
with app.app_context():
    db.create_all()

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
            "id": request_id,
            "start": start,
            "end": end,
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
        "id": request_id,
        "start": start,
        "end": end,
        "delta": (end - start).microseconds,
        "status": True,
    })

    return jsonify(response), 200

def save_result(result):
    response = Response(
        id=result['id'],
        start=result['start'],
        end=result['end'],
        delta=result['delta'],
        status=result['status']
    )
    
    try:
        db.session.add(response)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error saving to database: {e}")
