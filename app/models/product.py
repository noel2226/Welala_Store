"""
SQLAlchemy models for product management.
Supports both books and general goods with flexible schema.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, Text
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.database import Base


class ProductCategory(str, enum.Enum):
    """Product category enumeration."""
    BOOK = "book"
    GENERAL_GOOD = "general_good"


class Product(Base):
    """
    Product model representing items in the ecommerce store.
    
    Attributes:
        id: Primary key
        title: Product title (required)
        description: Product description
        price: Product price (required)
        stock: Available quantity (required)
        category: Product category (book or general_good)
        author: Author name (optional, for books)
        isbn: ISBN code (optional, for books)
        weight: Weight in kg (optional, for general goods)
        dimensions: Dimensions description (optional, for general goods)
        created_at: Timestamp of creation
        updated_at: Timestamp of last update
    """
    
    __tablename__ = "products"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Common fields
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False, index=True)
    stock = Column(Integer, nullable=False, default=0)
    category = Column(Enum(ProductCategory), nullable=False, index=True)
    
    # Book-specific fields
    author = Column(String(255), nullable=True)
    isbn = Column(String(20), nullable=True, unique=True)
    
    # General goods fields
    weight = Column(Float, nullable=True)  # in kg
    dimensions = Column(String(255), nullable=True)  # e.g., "10x20x5 cm"
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self) -> str:
        return f"<Product(id={self.id}, title='{self.title}', category={self.category})>"
