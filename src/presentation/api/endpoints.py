"""
FastAPI endpoints for PDF Price Search.

This module defines all API endpoints for the application.
"""

import time
import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from ...application.use_cases.search_price_use_case import SearchPriceUseCase
from ...application.use_cases.list_services_use_case import ListServicesUseCase
from ...application.use_cases.load_data_use_case import LoadDataUseCase
from ...application.services.price_search_service import PriceSearchService
from ..validation import InputValidator

from .models import (
    SearchRequest,
    SearchResponse,
    ServiceResponse,
    ServicesListResponse,
    ServicesSummaryResponse,
    LoadRequest,
    LoadResponse,
    HealthResponse,
    CacheStatsResponse,
    ErrorResponse,
)
from .dependencies import (
    get_search_use_case,
    get_list_use_case,
    get_load_use_case,
    get_search_service,
    get_app_container,
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


@router.post("/search", response_model=SearchResponse, tags=["Search"])
async def search_price(
    request: SearchRequest,
    use_case: SearchPriceUseCase = Depends(get_search_use_case)
):
    """
    Search for a shipping price.

    Executes a natural language search query to find shipping prices
    in the loaded PDF documents.

    - **query**: Natural language search query (e.g., "FedEx 2Day, Zone 5, 3 lb")
    - **use_cache**: Whether to use cached results (default: True)

    Returns the price information if found, or error details if not found.
    """
    try:
        # Validate query
        validated_query = InputValidator.validate_query(request.query)

        # Execute search
        logger.info(f"API search request: {validated_query}")
        response = use_case.execute(validated_query, use_cache=request.use_cache)

        # Convert to API response model
        return SearchResponse(
            success=response.success,
            price=response.price,
            currency=response.currency,
            service=response.service,
            zone=response.zone,
            weight=response.weight,
            source_document=response.source_document,
            error_message=response.error_message,
            search_time_ms=response.search_time_ms
        )

    except Exception as e:
        logger.error(f"Search failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.get("/services", response_model=ServicesListResponse, tags=["Services"])
async def list_services(
    use_case: ListServicesUseCase = Depends(get_list_use_case)
):
    """
    List all available shipping services.

    Returns a list of all services loaded from PDF documents,
    including their zones and weight ranges.
    """
    try:
        services = use_case.execute()

        # Convert to API response models
        service_responses = [
            ServiceResponse(
                name=s.name,
                available_zones=s.available_zones,
                min_weight=s.min_weight,
                max_weight=s.max_weight,
                source_pdf=s.source_pdf
            )
            for s in services
        ]

        return ServicesListResponse(
            services=service_responses,
            total_count=len(service_responses)
        )

    except Exception as e:
        logger.error(f"Failed to list services: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list services: {str(e)}"
        )


@router.get("/services/summary", response_model=ServicesSummaryResponse, tags=["Services"])
async def get_services_summary(
    use_case: ListServicesUseCase = Depends(get_list_use_case)
):
    """
    Get summary of available services.

    Returns aggregate information about all loaded services,
    including total count, available zones, and weight ranges.
    """
    try:
        summary = use_case.execute_summary()

        return ServicesSummaryResponse(
            total_services=summary['total_services'],
            available_zones=summary['available_zones'],
            weight_range=summary['weight_range']
        )

    except Exception as e:
        logger.error(f"Failed to get summary: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get summary: {str(e)}"
        )


@router.get("/services/{service_name}", response_model=ServiceResponse, tags=["Services"])
async def get_service_details(
    service_name: str,
    use_case: ListServicesUseCase = Depends(get_list_use_case)
):
    """
    Get details for a specific service.

    Returns detailed information about a single service by name.
    """
    try:
        services = use_case.execute()

        # Find matching service (case-insensitive)
        matching_service = None
        for service in services:
            if service.name.lower() == service_name.lower():
                matching_service = service
                break

        if not matching_service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Service not found: {service_name}"
            )

        return ServiceResponse(
            name=matching_service.name,
            available_zones=matching_service.available_zones,
            min_weight=matching_service.min_weight,
            max_weight=matching_service.max_weight,
            source_pdf=matching_service.source_pdf
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get service details: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get service details: {str(e)}"
        )


@router.post("/load", response_model=LoadResponse, tags=["Data"])
async def load_pdfs(
    request: LoadRequest,
    use_case: LoadDataUseCase = Depends(get_load_use_case)
):
    """
    Load PDF files from a directory.

    Loads pricing data from PDF files in the specified directory.
    If no directory is provided, uses the default directory from configuration.

    - **directory**: Path to directory containing PDFs (optional)
    - **recursive**: Whether to search subdirectories (default: False)
    """
    try:
        start_time = time.time()

        # Validate directory if provided
        if request.directory:
            InputValidator.validate_directory_path(request.directory)
            result = use_case.execute(request.directory, recursive=request.recursive)
        else:
            result = use_case.execute_default()

        elapsed = time.time() - start_time

        return LoadResponse(
            success=result['success'],
            total_files=result['total_files'],
            loaded_count=result['loaded_count'],
            failed_count=result['failed_count'],
            failed_files=result['failed_files'],
            load_time_seconds=elapsed
        )

    except Exception as e:
        logger.error(f"Failed to load PDFs: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load PDFs: {str(e)}"
        )


@router.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check(
    use_case: ListServicesUseCase = Depends(get_list_use_case)
):
    """
    Health check endpoint.

    Returns the current status of the application, including
    version information and loaded services count.
    """
    try:
        from ...application.config import get_config

        config = get_config()
        services = use_case.execute()

        return HealthResponse(
            status="healthy",
            version="1.0.0",
            services_loaded=len(services),
            cache_enabled=config.enable_cache
        )

    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return HealthResponse(
            status="unhealthy",
            version="1.0.0",
            services_loaded=0,
            cache_enabled=False
        )


@router.get("/cache/stats", response_model=CacheStatsResponse, tags=["Cache"])
async def get_cache_stats(
    service: PriceSearchService = Depends(get_search_service)
):
    """
    Get cache statistics.

    Returns information about the search cache, including
    hit rate and number of cached entries.
    """
    try:
        cache = service.cache

        if not cache:
            return CacheStatsResponse(
                enabled=False,
                size=0,
                hits=0,
                misses=0,
                hit_rate=0.0
            )

        stats = cache.get_stats()

        # Note: Current cache implementation doesn't track hits/misses
        # Return size information instead
        return CacheStatsResponse(
            enabled=True,
            size=stats.get('active_entries', 0),
            hits=0,
            misses=0,
            hit_rate=0.0
        )

    except Exception as e:
        logger.error(f"Failed to get cache stats: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get cache stats: {str(e)}"
        )


@router.delete("/cache", tags=["Cache"])
async def clear_cache(
    service: PriceSearchService = Depends(get_search_service)
):
    """
    Clear the search cache.

    Removes all cached search results.
    """
    try:
        cache = service.cache

        if not cache:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cache is not enabled"
            )

        cache.clear()

        return {"message": "Cache cleared successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to clear cache: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear cache: {str(e)}"
        )
