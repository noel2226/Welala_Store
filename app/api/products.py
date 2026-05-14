"""
Product API endpoints.
Provides CRUD operations for managing products in the ecommerce store.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional
import logging

from app.database import get_db
from app.models.product import Product, ProductCategory
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductListResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=ProductListResponse, status_code=status.HTTP_200_OK)
def list_products(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of items to return"),
    category: Optional[str] = Query(None, description="Filter by category: 'book' or 'general_good'"),
    search: Optional[str] = Query(None, description="Search in title and description"),
    db: Session = Depends(get_db),
) -> ProductListResponse:
    """
    Retrieve a paginated list of all products.
    
    Query Parameters:
    - skip: Number of items to skip (default: 0)
    - limit: Number of items to return (default: 10, max: 100)
    - category: Filter by category ('book' or 'general_good')
    - search: Search query for title or description
    
    Returns:
    - ProductListResponse: Paginated list of products
    """
    try:
        query = db.query(Product)
        
        # Apply category filter
        if category:
            try:
                category_enum = ProductCategory(category)
                query = query.filter(Product.category == category_enum)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid category. Must be 'book' or 'general_good'"
                )
        
        # Apply search filter
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Product.title.ilike(search_term),
                    Product.description.ilike(search_term)
                )
            )
        
        # Get total count before pagination
        total = query.count()
        
        # Apply pagination
        products = query.offset(skip).limit(limit).all()
        
        logger.info(f"Retrieved {len(products)} products (skip={skip}, limit={limit})")
        
        return ProductListResponse(
            total=total,
            skip=skip,
            limit=limit,
            data=[ProductResponse.from_orm(product) for product in products]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving products: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve products"
        )


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
) -> ProductResponse:
    """
    Create a new product.
    
    Request Body:
    - title: Product title (required)
    - price: Product price (required, > 0)
    - stock: Available quantity (required, >= 0)
    - category: 'book' or 'general_good' (required)
    - description: Product description (optional)
    - author: Author name (optional, for books only)
    - isbn: ISBN code (optional, for books only)
    - weight: Weight in kg (optional, for general goods only)
    - dimensions: Dimensions (optional, for general goods only)
    
    Returns:
    - ProductResponse: Created product
    
    Raises:
    - 400: Invalid input data
    - 409: ISBN already exists (for books)
    - 500: Internal server error
    """
    try:
        # Check for duplicate ISBN if provided
        if product.isbn:
            existing = db.query(Product).filter(Product.isbn == product.isbn).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Product with ISBN '{product.isbn}' already exists"
                )
        
        # Create new product
        db_product = Product(
            title=product.title,
            description=product.description,
            price=product.price,
            stock=product.stock,
            category=product.category,
            author=product.author,
            isbn=product.isbn,
            weight=product.weight,
            dimensions=product.dimensions,
        )
        
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        
        logger.info(f"Product created: id={db_product.id}, title='{db_product.title}'")
        
        return ProductResponse.from_orm(db_product)
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating product: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create product"
        )


@router.get("/{product_id}", response_model=ProductResponse, status_code=status.HTTP_200_OK)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
) -> ProductResponse:
    """
    Retrieve a specific product by ID.
    
    Path Parameters:
    - product_id: The product ID
    
    Returns:
    - ProductResponse: Product details
    
    Raises:
    - 404: Product not found
    - 500: Internal server error
    """
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {product_id} not found"
            )
        
        logger.info(f"Retrieved product: id={product_id}")
        
        return ProductResponse.from_orm(product)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving product {product_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve product"
        )


@router.patch("/{product_id}", response_model=ProductResponse, status_code=status.HTTP_200_OK)
def update_product(
    product_id: int,
    product_update: ProductUpdate,
    db: Session = Depends(get_db),
) -> ProductResponse:
    """
    Update an existing product.
    
    Path Parameters:
    - product_id: The product ID
    
    Request Body:
    - All fields are optional; only provided fields will be updated
    
    Returns:
    - ProductResponse: Updated product
    
    Raises:
    - 404: Product not found
    - 409: ISBN already exists (when updating ISBN)
    - 500: Internal server error
    """
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {product_id} not found"
            )
        
        # Check for duplicate ISBN if being updated
        if product_update.isbn and product_update.isbn != product.isbn:
            existing = db.query(Product).filter(Product.isbn == product_update.isbn).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Product with ISBN '{product_update.isbn}' already exists"
                )
        
        # Update only provided fields
        update_data = product_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(product, field, value)
        
        db.add(product)
        db.commit()
        db.refresh(product)
        
        logger.info(f"Product updated: id={product_id}")
        
        return ProductResponse.from_orm(product)
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating product {product_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update product"
        )


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
) -> None:
    """
    Delete a product.
    
    Path Parameters:
    - product_id: The product ID
    
    Returns:
    - 204 No Content on success
    
    Raises:
    - 404: Product not found
    - 500: Internal server error
    """
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {product_id} not found"
            )
        
        db.delete(product)
        db.commit()
        
        logger.info(f"Product deleted: id={product_id}")
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting product {product_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete product"
        )
