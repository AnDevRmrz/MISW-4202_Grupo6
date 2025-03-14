from flask import Flask, request, jsonify
import logging
import json
from datetime import datetime
import os
import uuid

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Archivo para guardar los logs de las solicitudes
log_file = './inventory_requests.log'

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint para verificar la salud del servicio"""
    return jsonify({"status": "healthy", "service": "inventory"}), 200

@app.route('/')
def index():
    """Página de inicio del servicio"""
    return jsonify({
        "service": "Inventory Service",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }), 200

@app.route('/product/<uuid:product_id>', methods=['POST, PUT'])
def update_product(product_id):
    """
    Endpoint para actualizar un producto.
    Simplemente registra la solicitud y devuelve 200.
    """
    product_id_str = str(product_id)
    timestamp = datetime.now().isoformat()
    
    try:
        # Extraemos los datos de la solicitud
        data = request.form.to_dict()
        
        # Registramos la solicitud
        app.logger.info(f"Recibida solicitud para producto {product_id_str}")
        
        # Guardamos los detalles de la solicitud en el archivo de log
        log_entry = {
            "timestamp": timestamp,
            "product_id": product_id_str,
            "data": data,
            "remote_addr": request.remote_addr,
            "method": request.method,
            "path": request.path
        }
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        # Respondemos con éxito
        return jsonify({
            "message": "Solicitud procesada correctamente",
            "product_id": product_id_str,
            "timestamp": timestamp,
            "status": "success"
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error al procesar la solicitud: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 