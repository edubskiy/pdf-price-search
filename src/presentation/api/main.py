"""
FastAPI application for PDF Price Search.

This module configures and initializes the FastAPI application
with all routes, middleware, and event handlers.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from ...application.config import get_config
from ...application.exceptions import ApplicationException
from ..validation.input_validator import ValidationError

from .endpoints import router
from .dependencies import get_app_container, get_load_use_case
from .models import ErrorResponse

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.

    This function handles initialization and cleanup tasks
    for the FastAPI application.
    """
    # Startup
    logger.info("Starting PDF Price Search API...")

    try:
        # Ensure container is ready
        container = get_app_container()
        logger.info("Application container initialized")

        # Auto-load PDFs on startup
        config = get_config()
        logger.info(f"Auto-loading PDFs from: {config.default_pdf_directory}")

        # Get load use case and execute
        load_use_case = container.load_data_use_case()
        result = load_use_case.execute_default()

        if result['success']:
            logger.info(
                f"Successfully loaded {result['loaded_count']} PDF files "
                f"(failed: {result['failed_count']})"
            )
        else:
            logger.warning("No PDF files were loaded on startup")

    except Exception as e:
        logger.error(f"Startup error: {e}", exc_info=True)
        # Continue anyway - allow API to start even if PDFs fail to load

    logger.info("PDF Price Search API started successfully")

    yield

    # Shutdown
    logger.info("Shutting down PDF Price Search API...")


# Create FastAPI application
app = FastAPI(
    title="PDF Price Search API",
    description="""
    ## PDF Price Search API

    This API allows you to search for shipping prices across multiple PDF documents
    using natural language queries.

    ### Features

    - **Search**: Natural language price search
    - **Services**: List available shipping services
    - **Load**: Load PDF files dynamically
    - **Cache**: Manage search cache for performance
    - **Health**: Monitor application status

    ### Example Query

    ```
    POST /search
    {
        "query": "FedEx 2Day, Zone 5, 3 lb",
        "use_cache": true
    }
    ```
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers

@app.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError):
    """Handle validation errors."""
    logger.warning(f"Validation error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ErrorResponse(
            error="ValidationError",
            message=str(exc),
            details=None
        ).model_dump()
    )


@app.exception_handler(ApplicationException)
async def application_error_handler(request: Request, exc: ApplicationException):
    """Handle application-level errors."""
    logger.error(f"Application error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="ApplicationError",
            message=str(exc),
            details=None
        ).model_dump()
    )


@app.exception_handler(RequestValidationError)
async def request_validation_error_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors."""
    logger.warning(f"Request validation error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            error="RequestValidationError",
            message="Invalid request data",
            details={"errors": exc.errors()}
        ).model_dump()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="InternalServerError",
            message="An unexpected error occurred",
            details=None
        ).model_dump()
    )


# Include routers
app.include_router(router, prefix="/api/v1")


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint.

    Returns basic API information and links to documentation.
    """
    return {
        "name": "PDF Price Search API",
        "version": "1.0.0",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        },
        "endpoints": {
            "search": "/api/v1/search",
            "services": "/api/v1/services",
            "health": "/api/v1/health"
        }
    }
