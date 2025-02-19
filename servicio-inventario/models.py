from sqlalchemy import Column, Integer, String
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

from random import randint

class Base(DeclarativeBase):
  pass

class Inventory(Base):
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    product_id = Column(Integer, unique=True, nullable=False)
    quantity = Column(Integer, nullable=False)

def populate(number_of_products=10):
    # Every time that the database is populated, we need to "restart" it
    db.drop_all() 
    db.create_all() 

    for i in range(1, number_of_products):
        random_quantity = randint(0, 500)
        product = Inventory(name=f"Product {i}", product_id=i, quantity=random_quantity)
        db.session.add(product)
    db.session.commit()

db = SQLAlchemy(model_class=Base)