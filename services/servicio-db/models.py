from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Response(db.Model):
    __tablename__ = 'responses'

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    request_id = db.Column(db.String(36), index=True)
    start = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime, nullable=False)
    delta = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Boolean, nullable=False)

    def to_dict(self):
        return {
            'response_id': self.request_Id,
            'id': self.id,
            'start': self.start.isoformat(),
            'end': self.end.isoformat(),
            'delta': self.delta,
            'status': self.status
        }
    
class Request(db.Model):
    __tablename__ = 'requests'

    id = db.Column(db.String(36), primary_key=True)
    start = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime, nullable=False)
    delta = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Boolean, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'start': self.start.isoformat(),
            'end': self.end.isoformat(),
            'delta': self.delta,
            'status': self.status
        }
