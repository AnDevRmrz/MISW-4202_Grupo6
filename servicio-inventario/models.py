from sqlalchemy import Column, Integer, String
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
  pass

class Inventory(Base):
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    product_id = Column(Integer, unique=True, nullable=False)
    quantity = Column(Integer, nullable=False)

db = SQLAlchemy(model_class=Base)