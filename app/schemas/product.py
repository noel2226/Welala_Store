"""
Pydantic schemas for product validation and serialization.
Provides type-safe request/response handling with detailed validation.
"""

from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, Literal
from enum import Enum


class ProductCategory(str, Enum):
    """Product category enumeration for schema."""
    BOOK = "book"
    GENERAL_GOOD = "general_good"


class ProductCreate(BaseModel):
    """Schema for creating a new product."""
    
    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Product title"
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Product description"
    )
    price: float = Field(
        ...,
        gt=0,
        description="Product price (must be greater than 0)"
    )
    stock: int = Field(
        ...,
        ge=0,
        description="Available stock quantity"
    )
    category: ProductCategory = Field(
        ...,
        description="Product category: 'book' or 'general_good'"
    )
    
    # Book-specific fields
    author: Optional[str] = Field(
        None,
        max_length=255,
        description="Author name (for books)"
    )
    isbn: Optional[str] = Field(
        None,
        max_length=20,
        description="ISBN code (for books)"
    )
    
    # General goods fields
    weight: Optional[float] = Field(
        None,
        gt=0,
        description="Weight in kg (for general goods)"
    )
    dimensions: Optional[str] = Field(
        None,
        max_length=255,
        description="Dimensions (for general goods)"
    )
    
    @field_validator('category')
    @classmethod
    def validate_category(cls, v):
        """Validate product category."""
        if v not in [ProductCategory.BOOK, ProductCategory.GENERAL_GOOD]:
            raise ValueError(f"Category must be '{ProductCategory.BOOK}' or '{ProductCategory.GENERAL_GOOD}'")
        return v
    
    @field_validator('author')
    @classmethod
    def author_requires_book(cls, v, info):
        """Validate that author is only provided for books."""
        if v is not None and info.data.get('category') != ProductCategory.BOOK:
            raise ValueError("Author field is only valid for books")
        return v
    
    @field_validator('isbn')
    @classmethod
    def isbn_requires_book(cls, v, info):
        """Validate that ISBN is only provided for books."""
        if v is not None and info.data.get('category') != ProductCategory.BOOK:
            raise ValueError("ISBN field is only valid for books")
        return v
    
    @field_validator('weight')
    @classmethod
    def weight_requires_general_good(cls, v, info):
        """Validate that weight is only provided for general goods."""
        if v is not None and info.data.get('category') != ProductCategory.GENERAL_GOOD:
            raise ValueError("Weight field is only valid for general goods")
        return v
    
    @field_validator('dimensions')
    @classmethod
    def dimensions_requires_general_good(cls, v, info):
        """Validate that dimensions is only provided for general goods."""
        if v is not None and info.data.get('category') != ProductCategory.GENERAL_GOOD:
            raise ValueError("Dimensions field is only valid for general goods")
        return v


class ProductUpdate(BaseModel):
    """Schema for updating an existing product."""
    
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    price: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    author: Optional[str] = Field(None, max_length=255)
    isbn: Optional[str] = Field(None, max_length=20)
    weight: Optional[float] = Field(None, gt=0)
    dimensions: Optional[str] = Field(None, max_length=255)


class ProductResponse(BaseModel):
    """Schema for product responses (read-only)."""
    
    id: int = Field(..., description="Product ID")
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., description="Product price")
    stock: int = Field(..., description="Available stock")
    category: ProductCategory = Field(..., description="Product category")
    author: Optional[str] = Field(None, description="Author name (for books)")
    isbn: Optional[str] = Field(None, description="ISBN code (for books)")
    weight: Optional[float] = Field(None, description="Weight in kg (for general goods)")
    dimensions: Optional[str] = Field(None, description="Dimensions (for general goods)")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "title": "The Great Gatsby",
                "description": "A classic American novel",
                "price": 12.99,
                "stock": 50,
                "category": "book",
                "author": "F. Scott Fitzgerald",
                "isbn": "978-0-7432-7356-5",
                "weight": None,
                "dimensions": None,
                "created_at": "2024-01-15T10:30:00",
                "updated_at": "2024-01-15T10:30:00"
            }
        }
    }


class ProductListResponse(BaseModel):
    """Schema for paginated product list responses."""
    
    total: int = Field(..., description="Total number of products")
    skip: int = Field(..., description="Number of items skipped")
    limit: int = Field(..., description="Number of items returned")
    data: list[ProductResponse] = Field(..., description="List of products")
