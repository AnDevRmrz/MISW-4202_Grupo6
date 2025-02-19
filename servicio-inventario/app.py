from flask import Flask, jsonify
from models import db

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///inventory.db"

app_context = app.app_context()
app_context.push()

db.init_app(app)
db.create_all()

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/product/<int:product_id>", methods=["GET"])
def get_product_inventory(product_id: int):
    """Retrieve inventory for a specific product."""
    product = db_session.query(Inventory).filter_by(product_id=product_id).first()

    if not product:
        return jsonify({"error": "Product not found"}), 404

    response = {"product_id": product.product_id, "inventory": product.quantity}
    return jsonify(response), 200
