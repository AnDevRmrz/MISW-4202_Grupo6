from datetime import datetime

from sqlalchemy import inspect
from flask import Flask, request, jsonify
from models import Request, Response, db
from concurrent.futures import ThreadPoolExecutor
import threading

app = Flask(__name__)

# Configure SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///inventario.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)

# Thread-safe queue for writes
executor = ThreadPoolExecutor(max_workers=5)
lock = threading.Lock()

# Create tables within application context
with app.app_context():
    inspector = inspect(db.engine)
    if inspector.get_table_names():  # Check if there are any tables
        db.drop_all()
        db.session.commit()
    db.create_all()


@app.route("/insert", methods=["POST"])
def insert_data():
    data = request.json.copy()  # Copy data to avoid losing request context

    def db_insert(data):
        try:
            with app.app_context():
                with lock:
                    new_entry = None
                    if data["type"] == "request":
                        new_entry = Request(
                            id=data["id"],
                            start=datetime.fromisoformat(data["start"]),
                            end=datetime.fromisoformat(data["end"]),
                            delta=data["delta"],
                            status=data["status"],
                        )
                    elif data["type"] == "response":
                        app.logger.info("Response received")
                        new_entry = Response(
                            request_id=data["request_id"],
                            start=datetime.fromisoformat(data["start"]),
                            end=datetime.fromisoformat(data["end"]),
                            delta=data["delta"],
                            status=data["status"]
                        )

                    if new_entry:
                        db.session.add(new_entry)
                        db.session.commit()
                        app.logger.info(f"Saved entry: {new_entry}")
                    else:
                        app.logger.warning("No entry was created")

        except Exception as e:
            app.logger.error(f"Database insert failed: {str(e)}")

    # Queue the write operation
    executor.submit(db_insert, data)
    return jsonify({"message": "Insert scheduled"}), 202


@app.route("/report", methods=["GET"])
def get_data():
    query = db.session.query(Request, Response).join(
        Response, Request.id == Response.request_id).all()

    # Convert query result to a list of dictionaries
    results = [
        {
            "request.id": req.id,
            "request.start": req.start.isoformat(),
            "request.end": req.end.isoformat(),
            "request.delta": req.delta,
            "request.status": req.status,
            "response.start": res.start.isoformat(),
            "response.end": res.end.isoformat(),
            "response.delta": res.delta,
            "response.status": res.status,
        }
        for req, res in query
    ]

    return jsonify(results), 200
