import json
from flask import Flask, request, jsonify
import hashlib
import hmac
import os

app = Flask(__name__)

SECRET_KEY = os.getenv("SECRET_KEY", "mykeyishiddensomewhereinthecloud")

def generate_hmac(data: dict) -> str:
    json_data = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
    return hmac.new(SECRET_KEY.encode(), json_data.encode(), hashlib.sha256).hexdigest()

@app.route("/validate", methods=["POST"])
def validate_message():
    print("Using SECRET_KEY:", SECRET_KEY)
    try:
        request_data = request.get_json()
        
        if not request_data or "payload" not in request_data or "hash" not in request_data:
            return jsonify({"error": "Missing payload or hash"}), 400

        payload = request_data["payload"]
        received_hash = request_data["hash"]
        computed_hash = generate_hmac(payload)

        if hmac.compare_digest(received_hash, computed_hash):
            return jsonify({"message": "Valid payload", "status": "success"}), 200
        else:
            return jsonify({"error": "Invalid hash", "status": "failure"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500