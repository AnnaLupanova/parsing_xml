from database import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Date, Integer, Float, ForeignKey


class Sale(Base):
    __tablename__ = 'sales'
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, unique=True)
    products = relationship("Product", back_populates="sale", lazy="selectin")


class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    quantity = Column(Integer)
    price = Column(Float)
    category = Column(String)
    sale_id = Column(Integer, ForeignKey('sales.id'))
    sale = relationship("Sale", back_populates="products")


