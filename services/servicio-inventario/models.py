from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

class Response(db.Model):
    __tablename__ = 'responses'
    
    response_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    id = db.Column(db.String(36), nullable=False, index=True)
    start = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime, nullable=False)
    delta = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Boolean, nullable=False)

    def to_dict(self):
        return {
            'response_id': self.response_id,
            'id': self.id,
            'start': self.start.isoformat(),
            'end': self.end.isoformat(),
            'delta': self.delta,
            'status': self.status
        } 