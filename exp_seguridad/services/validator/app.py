import json
from flask import Flask, request, jsonify
import hashlib
import hmac
import os
import requests
import urllib.parse
import logging
import csv
from datetime import datetime
import uuid

app = Flask(__name__)

filename = './validation_records.csv'
headers = ["id", "start", "end", "delta", "valid_content", "status"]

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SECRET_KEY = os.getenv("SECRET_KEY", "mykeyishiddensomewhereinthecloud")

def generate_hmac(data: dict) -> str:
    json_data = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
    return hmac.new(SECRET_KEY.encode(), json_data.encode(), hashlib.sha256).hexdigest()

# Function to write validation records to CSV
def write_validation_record(id, start, valid_content, status):
    end_time = datetime.now()
    delta = (end_time - start).microseconds
    
    # Create the file with headers if it doesn't exist
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
    
    # Append the new record
    with open(filename, "a") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        record = {
            "id": id,
            "start": start,
            "end": end_time,
            "delta": delta,
            "valid_content": valid_content,
            "status": status
        }
        writer.writerow(record)
        logger.info(f"Validation record written: {record}")
    

@app.route("/validate-and-forward", methods=["GET"])
def validate_and_forward():
    try:
        start_time = datetime.now()
        
        # Get parameters from query string
        target = request.args.get("target", "")
        product_id = request.args.get("product_id", "")
        payload_str = request.args.get("payload", "{}")
        received_hash = request.args.get("hash", "")
        id = product_id
        
        logger.info(f"Validating request for target: {target}, product_id: {product_id}")
        logger.info(f"Payload: {payload_str}")
        logger.info(f"Hash: {received_hash}")
        
        # Parse the payload JSON
        try:
            payload = json.loads(urllib.parse.unquote(payload_str))
        except json.JSONDecodeError:
            logger.error("Invalid JSON payload")
            write_validation_record(id, start_time, False,"400 Invalid JSON payload")
            return jsonify({"error": "Invalid JSON payload"}), 400
        
        # Validate the hash
        computed_hash = generate_hmac(payload)
        is_valid = hmac.compare_digest(received_hash, computed_hash)
        
        if not is_valid:
            logger.warning(f"Invalid hash. Expected: {computed_hash}, Received: {received_hash}")
            write_validation_record(id, start_time, False, "400 Invalid hash")
            return jsonify({"error": "Invalid hash", "status": "failure"}), 400
        
        # If validation passes, forward to the target service
        if target == "inventory":
            target_url = f"http://inventory:5000/product/{product_id}"
            forward_data = {
                "payload": payload,
                "hash": received_hash
            }
            
            logger.info(f"Forwarding to: {target_url}")
            response = requests.put(
                target_url,
                json=forward_data,
                headers={"Content-Type": "application/json"}
            )
            
            status = f"Forwarded with status {response.status_code}"
            write_validation_record(id, start_time, True, status)
            
            return (
                response.content,
                response.status_code,
                {'Content-Type': response.headers.get('Content-Type', 'application/json')}
            )
        else:
            status = f"Unknown target service: {target}"
            write_validation_record(id, start_time, False, status)
            return jsonify({"error": status}), 400
    
    except Exception as e:
        logger.error(f"Error in validate-and-forward: {str(e)}")
        try:
            write_validation_record(id, start_time, False, f"Error: {str(e)}")
        except:
            logger.error("Failed to write validation record")
        return jsonify({"error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "service": "validator"}), 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)