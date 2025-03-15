from flask import Flask, request, jsonify
import logging
import json
from datetime import datetime
import os

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint to check service health"""
    return jsonify({"status": "healthy", "service": "inventory"}), 200

@app.route('/')
def index():
    """Service home page"""
    return jsonify({
        "service": "Inventory Service",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }), 200

@app.route('/product/<product_id>', methods=['POST', 'PUT', 'GET'])
def update_product(product_id):
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)