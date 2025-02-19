from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/product/<int:product_id>', methods=['GET'])
def get_product_invetory(product_id: int):
    response = {
        'product_id': product_id,
        'inventory': 100
    }

    return jsonify(response), 200