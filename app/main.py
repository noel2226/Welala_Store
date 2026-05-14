"""
FastAPI application factory and configuration.
Initializes the API with routes, middleware, and documentation.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.config import get_settings
from app.database import init_db
from app.utils import setup_logging
from app.api import router

logger = logging.getLogger(__name__)

settings = get_settings()


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        FastAPI: Configured application instance
    """
    
    # Setup logging
    setup_logging(debug=settings.debug)
    
    # Create FastAPI app
    app = FastAPI(
        title=settings.api_title,
        description=settings.api_description,
        version=settings.api_version,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify allowed origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Initialize database
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise
    
    # Include routers
    app.include_router(router)
    
    # Root endpoint
    @app.get("/", tags=["root"])
    def read_root():
        """Root endpoint with API information."""
        return {
            "name": settings.api_title,
            "version": settings.api_version,
            "description": settings.api_description,
            "docs": "/docs",
            "redoc": "/redoc",
        }
    
    # Health check endpoint
    @app.get("/health", tags=["health"])
    def health_check():
        """Health check endpoint."""
        return {"status": "healthy"}
    
    logger.info(f"FastAPI application initialized: {settings.api_title} v{settings.api_version}")
    
    return app


# Create app instance
app = create_app()
