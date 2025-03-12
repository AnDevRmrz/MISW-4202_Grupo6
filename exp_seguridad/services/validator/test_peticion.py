import requests
import hashlib
import hmac
import json

# Configuración
SECRET_KEY = "mykeyishiddensomewhereinthecloud"
PAYLOAD = {"order_id": 123, "items": ["producto1", "producto2"]}

# Generar hash HMAC-SHA256
def generate_hmac(data: dict, key: str) -> str:
    json_data = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
    return hmac.new(key.encode(), json_data.encode(), hashlib.sha256).hexdigest()

HASH = generate_hmac(PAYLOAD, SECRET_KEY)

# Enviar solicitud al microservicio
url = "http://127.0.0.1:5000/validate"
headers = {"Content-Type": "application/json"}
payload = json.dumps({"payload": PAYLOAD, "hash": HASH})

response = requests.post(url, headers=headers, data=payload)

# Mostrar respuesta
print("Payload:", PAYLOAD)
print("Generated Hash:", HASH)
print("Response:", response.status_code, response.json())