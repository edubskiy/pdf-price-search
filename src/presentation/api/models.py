"""
Pydantic models for the API layer.

This module defines request and response models for the FastAPI application.
"""

from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


class SearchRequest(BaseModel):
    """Request model for price search."""

    query: str = Field(
        ...,
        description="Search query in natural language",
        min_length=1,
        max_length=500,
        examples=["FedEx 2Day, Zone 5, 3 lb"]
    )

    use_cache: bool = Field(
        True,
        description="Whether to use cached results"
    )

    @field_validator('query')
    @classmethod
    def validate_query(cls, v: str) -> str:
        """Validate and strip query."""
        return v.strip()


class SearchResponse(BaseModel):
    """Response model for price search."""

    success: bool = Field(..., description="Whether the search was successful")
    price: Optional[Decimal] = Field(None, description="The found price")
    currency: str = Field("USD", description="Currency code")
    service: Optional[str] = Field(None, description="Matched service name")
    zone: Optional[int] = Field(None, description="Zone number")
    weight: Optional[float] = Field(None, description="Weight in pounds")
    source_document: Optional[str] = Field(None, description="Source PDF file")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    search_time_ms: float = Field(..., description="Search time in milliseconds")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "success": True,
                    "price": "29.50",
                    "currency": "USD",
                    "service": "FedEx 2Day",
                    "zone": 5,
                    "weight": 3.0,
                    "source_document": "FedEx_Standard_List_Rates_2025.pdf",
                    "error_message": None,
                    "search_time_ms": 45.2
                }
            ]
        }
    }


class ServiceResponse(BaseModel):
    """Response model for service information."""

    name: str = Field(..., description="Service name")
    available_zones: List[int] = Field(..., description="Available zones")
    min_weight: float = Field(..., description="Minimum weight in pounds")
    max_weight: float = Field(..., description="Maximum weight in pounds")
    source_pdf: str = Field(..., description="Source PDF file path")


class ServicesListResponse(BaseModel):
    """Response model for list of services."""

    services: List[ServiceResponse] = Field(..., description="List of available services")
    total_count: int = Field(..., description="Total number of services")


class ServicesSummaryResponse(BaseModel):
    """Response model for services summary."""

    total_services: int = Field(..., description="Total number of services")
    available_zones: List[int] = Field(..., description="All available zones")
    weight_range: dict = Field(..., description="Overall weight range")


class LoadRequest(BaseModel):
    """Request model for loading PDF files."""

    directory: Optional[str] = Field(
        None,
        description="Directory path (uses default if not provided)"
    )

    recursive: bool = Field(
        False,
        description="Search subdirectories recursively"
    )


class LoadResponse(BaseModel):
    """Response model for load operation."""

    success: bool = Field(..., description="Whether loading was successful")
    total_files: int = Field(..., description="Total number of files found")
    loaded_count: int = Field(..., description="Number of successfully loaded files")
    failed_count: int = Field(..., description="Number of failed files")
    failed_files: List[dict] = Field(
        default_factory=list,
        description="List of failed files with errors"
    )
    load_time_seconds: float = Field(..., description="Time taken to load in seconds")


class HealthResponse(BaseModel):
    """Response model for health check."""

    status: str = Field(..., description="Service status", examples=["healthy"])
    version: str = Field(..., description="Application version")
    services_loaded: int = Field(..., description="Number of loaded services")
    cache_enabled: bool = Field(..., description="Whether caching is enabled")


class CacheStatsResponse(BaseModel):
    """Response model for cache statistics."""

    enabled: bool = Field(..., description="Whether cache is enabled")
    size: int = Field(0, description="Number of cached entries")
    hits: int = Field(0, description="Cache hits")
    misses: int = Field(0, description="Cache misses")
    hit_rate: float = Field(0.0, description="Cache hit rate percentage")


class ErrorResponse(BaseModel):
    """Response model for errors."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[dict] = Field(None, description="Additional error details")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "error": "ValidationError",
                    "message": "Invalid query format",
                    "details": {"field": "query", "issue": "contains invalid characters"}
                }
            ]
        }
    }
