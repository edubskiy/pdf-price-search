# API Documentation

## Overview

The PDF Price Search API is a RESTful API built with FastAPI that provides endpoints for searching shipping prices, managing services, and loading PDF data.

**Base URL**: `http://localhost:8000/api`

**API Documentation**:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Table of Contents

1. [Authentication](#authentication)
2. [Endpoints](#endpoints)
3. [Request/Response Models](#requestresponse-models)
4. [Error Handling](#error-handling)
5. [Examples](#examples)

## Authentication

Currently, the API does not require authentication. This may change in future versions.

## Endpoints

### Search

#### POST /api/search

Search for shipping prices using natural language queries.

**Request Body**:
```json
{
  "query": "FedEx 2Day, Zone 5, 3 lb",
  "use_cache": true
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "price": 25.50,
  "currency": "USD",
  "service": "FedEx 2Day",
  "zone": 5,
  "weight": 3.0,
  "source_document": "fedex_rates.pdf",
  "error_message": null,
  "search_time_ms": 15.2
}
```

**Response** (Not Found):
```json
{
  "success": false,
  "price": null,
  "currency": null,
  "service": null,
  "zone": null,
  "weight": null,
  "source_document": null,
  "error_message": "No matching service found",
  "search_time_ms": 8.5
}
```

### Services

#### GET /api/services

List all available shipping services.

**Response** (200 OK):
```json
{
  "services": [
    {
      "name": "FedEx 2Day",
      "available_zones": [1, 2, 3, 4, 5, 6, 7, 8],
      "min_weight": 1.0,
      "max_weight": 70.0,
      "source_pdf": "fedex_rates.pdf"
    },
    {
      "name": "FedEx Standard Overnight",
      "available_zones": [1, 2, 3, 4, 5, 6, 7, 8],
      "min_weight": 1.0,
      "max_weight": 150.0,
      "source_pdf": "fedex_rates.pdf"
    }
  ],
  "total_count": 2
}
```

#### GET /api/services/summary

Get summary statistics of all services.

**Response** (200 OK):
```json
{
  "total_services": 10,
  "available_zones": [1, 2, 3, 4, 5, 6, 7, 8],
  "weight_range": {
    "min": 1.0,
    "max": 150.0
  }
}
```

#### GET /api/services/{service_name}

Get details for a specific service.

**Parameters**:
- `service_name` (path): Name of the service (URL-encoded)

**Example**: `/api/services/FedEx%202Day`

**Response** (200 OK):
```json
{
  "name": "FedEx 2Day",
  "available_zones": [1, 2, 3, 4, 5, 6, 7, 8],
  "min_weight": 1.0,
  "max_weight": 70.0,
  "source_pdf": "fedex_rates.pdf"
}
```

**Response** (404 Not Found):
```json
{
  "detail": "Service not found: Unknown Service"
}
```

### Data Loading

#### POST /api/load

Load PDF files from a directory.

**Request Body**:
```json
{
  "directory": "/path/to/pdfs",
  "recursive": false
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "total_files": 5,
  "loaded_count": 4,
  "failed_count": 1,
  "failed_files": ["corrupted.pdf"],
  "load_time_seconds": 2.45
}
```

### System

#### GET /api/health

Health check endpoint.

**Response** (200 OK):
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services_loaded": 10,
  "cache_enabled": true
}
```

### Cache Management

#### GET /api/cache/stats

Get cache statistics.

**Response** (200 OK):
```json
{
  "enabled": true,
  "size": 25,
  "hits": 150,
  "misses": 25,
  "hit_rate": 0.857
}
```

#### DELETE /api/cache

Clear the search cache.

**Response** (200 OK):
```json
{
  "message": "Cache cleared successfully"
}
```

## Request/Response Models

### SearchRequest

```python
{
  "query": str,          # Natural language search query (required)
  "use_cache": bool      # Whether to use cache (default: true)
}
```

**Query Format Examples**:
- `"FedEx 2Day, Zone 5, 3 lb"`
- `"2 pounds to zone 5"`
- `"zone 8, 10lb"`
- `"5 lbs zone 3"`

### SearchResponse

```python
{
  "success": bool,                  # Whether search was successful
  "price": float | null,            # Price if found
  "currency": str | null,           # Currency code (e.g., "USD")
  "service": str | null,            # Service name
  "zone": int | null,               # Zone number (1-8)
  "weight": float | null,           # Weight in pounds
  "source_document": str | null,    # Source PDF filename
  "error_message": str | null,      # Error message if unsuccessful
  "search_time_ms": float           # Search execution time in ms
}
```

### ServiceResponse

```python
{
  "name": str,                      # Service name
  "available_zones": List[int],     # Available zones (e.g., [1, 2, 3, 4, 5, 6, 7, 8])
  "min_weight": float,              # Minimum weight in pounds
  "max_weight": float,              # Maximum weight in pounds
  "source_pdf": str                 # Source PDF filename
}
```

### LoadRequest

```python
{
  "directory": str | null,          # Directory path (optional, uses default if null)
  "recursive": bool                 # Search subdirectories (default: false)
}
```

### LoadResponse

```python
{
  "success": bool,                  # Overall success status
  "total_files": int,               # Total PDF files found
  "loaded_count": int,              # Successfully loaded files
  "failed_count": int,              # Failed files
  "failed_files": List[str],        # List of failed filenames
  "load_time_seconds": float        # Total load time in seconds
}
```

## Error Handling

### HTTP Status Codes

- **200 OK**: Request succeeded
- **400 Bad Request**: Invalid input parameters
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server error

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Errors

#### Invalid Query Format

**Status**: 400 Bad Request
```json
{
  "detail": "Invalid query format: query cannot be empty"
}
```

#### Service Not Found

**Status**: 404 Not Found
```json
{
  "detail": "Service not found: Unknown Service"
}
```

#### PDF Loading Error

**Status**: 500 Internal Server Error
```json
{
  "detail": "Failed to load PDFs: Directory not found"
}
```

## Examples

### Example 1: Basic Search

**Request**:
```bash
curl -X POST "http://localhost:8000/api/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "2lb to zone 5"}'
```

**Response**:
```json
{
  "success": true,
  "price": 18.25,
  "currency": "USD",
  "service": "FedEx Ground",
  "zone": 5,
  "weight": 2.0,
  "source_document": "fedex_rates.pdf",
  "error_message": null,
  "search_time_ms": 12.3
}
```

### Example 2: Search with Service Filter

**Request**:
```bash
curl -X POST "http://localhost:8000/api/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "FedEx 2Day, 5lb, zone 8"}'
```

**Response**:
```json
{
  "success": true,
  "price": 45.75,
  "currency": "USD",
  "service": "FedEx 2Day",
  "zone": 8,
  "weight": 5.0,
  "source_document": "fedex_rates.pdf",
  "error_message": null,
  "search_time_ms": 8.7
}
```

### Example 3: List All Services

**Request**:
```bash
curl -X GET "http://localhost:8000/api/services"
```

**Response**:
```json
{
  "services": [
    {
      "name": "FedEx 2Day",
      "available_zones": [1, 2, 3, 4, 5, 6, 7, 8],
      "min_weight": 1.0,
      "max_weight": 70.0,
      "source_pdf": "fedex_rates.pdf"
    }
  ],
  "total_count": 1
}
```

### Example 4: Load PDFs

**Request**:
```bash
curl -X POST "http://localhost:8000/api/load" \
  -H "Content-Type: application/json" \
  -d '{"directory": "/path/to/pdfs", "recursive": false}'
```

**Response**:
```json
{
  "success": true,
  "total_files": 3,
  "loaded_count": 3,
  "failed_count": 0,
  "failed_files": [],
  "load_time_seconds": 1.85
}
```

### Example 5: Health Check

**Request**:
```bash
curl -X GET "http://localhost:8000/api/health"
```

**Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services_loaded": 10,
  "cache_enabled": true
}
```

### Example 6: Clear Cache

**Request**:
```bash
curl -X DELETE "http://localhost:8000/api/cache"
```

**Response**:
```json
{
  "message": "Cache cleared successfully"
}
```

## Rate Limiting

Currently, there is no rate limiting implemented. This may be added in future versions.

## Versioning

The API is currently at version 1.0.0. Future versions may introduce breaking changes, which will be communicated in the changelog.

## Python Client Example

```python
import requests

# Base URL
BASE_URL = "http://localhost:8000/api"

# Search for a price
def search_price(query: str) -> dict:
    response = requests.post(
        f"{BASE_URL}/search",
        json={"query": query, "use_cache": True}
    )
    response.raise_for_status()
    return response.json()

# List services
def list_services() -> dict:
    response = requests.get(f"{BASE_URL}/services")
    response.raise_for_status()
    return response.json()

# Load PDFs
def load_pdfs(directory: str) -> dict:
    response = requests.post(
        f"{BASE_URL}/load",
        json={"directory": directory, "recursive": False}
    )
    response.raise_for_status()
    return response.json()

# Example usage
if __name__ == "__main__":
    # Search for a price
    result = search_price("2lb to zone 5")
    print(f"Price: ${result['price']}")

    # List all services
    services = list_services()
    print(f"Total services: {services['total_count']}")
```

## Best Practices

1. **Always validate input** - Check query format before sending
2. **Handle errors gracefully** - Check success field in responses
3. **Use caching** - Enable cache for better performance
4. **Check health** - Monitor /health endpoint
5. **Log requests** - Keep track of API usage

## Support

For issues or questions, please file an issue on the GitHub repository.
