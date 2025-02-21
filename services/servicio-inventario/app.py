from flask import Flask, jsonify
from models import db, populate, Inventory

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///inventory.db"

app_context = app.app_context()
app_context.push()

db.init_app(app)
populate(number_of_products=500)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/product/<int:product_id>", methods=["GET"])
def get_product_inventory(product_id: int):
    """Retrieve inventory for a specific product."""
    product = db.get_or_404(Inventory, product_id)

    if not product:
        return jsonify({"error": "Product not found"}), 404

    response = {
        "name": product.name,
        "product_id": product.product_id,
        "inventory": product.quantity,
    }

    return jsonify(response), 200
