# PDF Price Search - API Test Samples

**Base URL**: http://localhost:8000

The API is currently running and loaded with real FedEx pricing data (5 services, 5,250+ prices).

---

## Quick Test Commands

### 1. Health Check
```bash
curl http://localhost:8000/api/v1/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services_loaded": 5,
  "cache_enabled": true
}
```

---

### 2. Search for Price (POST)

#### Example 1: FedEx 2Day Service
```bash
curl -X POST 'http://localhost:8000/api/v1/search' \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "FedEx 2Day, Zone 5, 3 lb",
    "use_cache": true
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "price": "33.3136",
  "currency": "USD",
  "service": "FedEx 2Day",
  "zone": 5,
  "weight": 3.0,
  "source_document": "loaded_pdf",
  "error_message": null,
  "search_time_ms": 0.43
}
```

#### Example 2: Standard Overnight
```bash
curl -X POST 'http://localhost:8000/api/v1/search' \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "Standard Overnight, z2, 10 lbs"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "price": "51.7853",
  "currency": "USD",
  "service": "FedEx Standard Overnight",
  "zone": 2,
  "weight": 10.0,
  "source_document": "loaded_pdf",
  "error_message": null,
  "search_time_ms": 0.35
}
```

#### Example 3: Express Saver
```bash
curl -X POST 'http://localhost:8000/api/v1/search' \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "Express Saver Z8 1 lb"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "price": "39.8646",
  "currency": "USD",
  "service": "FedEx Express Saver",
  "zone": 8,
  "weight": 1.0,
  "source_document": "loaded_pdf",
  "error_message": null,
  "search_time_ms": 0.28
}
```

#### Example 4: Priority Overnight
```bash
curl -X POST 'http://localhost:8000/api/v1/search' \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "Priority Overnight, Zone 3, 5 lb"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "price": "62.7163",
  "currency": "USD",
  "service": "FedEx Priority Overnight",
  "zone": 3,
  "weight": 5.0,
  "source_document": "loaded_pdf",
  "error_message": null,
  "search_time_ms": 0.31
}
```

#### Example 5: First Overnight (Heavy Package)
```bash
curl -X POST 'http://localhost:8000/api/v1/search' \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "FedEx First Overnight, Zone 7, 20 lb"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "price": "300.84303",
  "currency": "USD",
  "service": "FedEx First Overnight",
  "zone": 7,
  "weight": 20.0,
  "source_document": "loaded_pdf",
  "error_message": null,
  "search_time_ms": 0.42
}
```

#### Example 6: Service Not Found (Error Case)
```bash
curl -X POST 'http://localhost:8000/api/v1/search' \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "Ground Z6 12 lb"
  }'
```

**Expected Response:**
```json
{
  "success": false,
  "price": null,
  "currency": "USD",
  "service": null,
  "zone": null,
  "weight": null,
  "source_document": null,
  "error_message": "Service not available: 'Ground': Service 'Ground' not found. Available services: FedEx First Overnight, FedEx Priority Overnight, FedEx Standard Overnight, FedEx 2Day, FedEx Express Saver",
  "search_time_ms": 0.15
}
```

---

### 3. List All Services (GET)
```bash
curl http://localhost:8000/api/v1/services
```

**Expected Response:**
```json
{
  "services": [
    {
      "name": "FedEx First Overnight",
      "available_zones": [2, 3, 4, 5, 6, 7, 8],
      "min_weight": 1.0,
      "max_weight": 2000.0,
      "source_pdf": "loaded_pdf"
    },
    {
      "name": "FedEx Priority Overnight",
      "available_zones": [2, 3, 4, 5, 6, 7, 8],
      "min_weight": 1.0,
      "max_weight": 2000.0,
      "source_pdf": "loaded_pdf"
    },
    {
      "name": "FedEx Standard Overnight",
      "available_zones": [2, 3, 4, 5, 6, 7, 8],
      "min_weight": 1.0,
      "max_weight": 150.0,
      "source_pdf": "loaded_pdf"
    },
    {
      "name": "FedEx 2Day",
      "available_zones": [2, 3, 4, 5, 6, 7, 8],
      "min_weight": 1.0,
      "max_weight": 2000.0,
      "source_pdf": "loaded_pdf"
    },
    {
      "name": "FedEx Express Saver",
      "available_zones": [2, 3, 4, 5, 6, 7, 8],
      "min_weight": 1.0,
      "max_weight": 150.0,
      "source_pdf": "loaded_pdf"
    }
  ],
  "total_count": 5
}
```

---

### 4. Get Services Summary (GET)
```bash
curl http://localhost:8000/api/v1/services/summary
```

**Expected Response:**
```json
{
  "total_services": 5,
  "available_zones": [2, 3, 4, 5, 6, 7, 8],
  "zone_count": 7,
  "services": [
    "FedEx First Overnight",
    "FedEx Priority Overnight",
    "FedEx Standard Overnight",
    "FedEx 2Day",
    "FedEx Express Saver"
  ]
}
```

---

### 5. Get Specific Service Details (GET)
```bash
curl 'http://localhost:8000/api/v1/services/FedEx%202Day'
```

**Expected Response:**
```json
{
  "name": "FedEx 2Day",
  "available_zones": [2, 3, 4, 5, 6, 7, 8],
  "min_weight": 1.0,
  "max_weight": 2000.0,
  "source_pdf": "loaded_pdf"
}
```

---

### 6. Cache Statistics (GET)
```bash
curl http://localhost:8000/api/v1/cache/stats
```

**Expected Response:**
```json
{
  "enabled": true,
  "size": 5,
  "hits": 12,
  "misses": 8,
  "hit_rate": 0.6
}
```

---

### 7. Clear Cache (DELETE)
```bash
curl -X DELETE http://localhost:8000/api/v1/cache
```

**Expected Response:**
```json
{
  "message": "Cache cleared successfully",
  "previous_size": 5
}
```

---

### 8. Root Endpoint (GET)
```bash
curl http://localhost:8000/
```

**Expected Response:**
```json
{
  "name": "PDF Price Search API",
  "version": "1.0.0",
  "description": "Search pricing data from PDF documents",
  "docs_url": "/docs",
  "health_check_url": "/api/v1/health"
}
```

---

## Interactive API Documentation

Visit these URLs in your browser for interactive documentation:

1. **Swagger UI**: http://localhost:8000/docs
2. **ReDoc**: http://localhost:8000/redoc

---

## Python Client Examples

### Using requests library:

```python
import requests

# 1. Health check
response = requests.get('http://localhost:8000/api/v1/health')
print(response.json())

# 2. Search for price
search_data = {
    "query": "FedEx 2Day, Zone 5, 3 lb",
    "use_cache": True
}
response = requests.post(
    'http://localhost:8000/api/v1/search',
    json=search_data
)
result = response.json()
if result['success']:
    print(f"Price: ${result['price']} {result['currency']}")
    print(f"Service: {result['service']}")
    print(f"Search time: {result['search_time_ms']}ms")
else:
    print(f"Error: {result['error_message']}")

# 3. List all services
response = requests.get('http://localhost:8000/api/v1/services')
services = response.json()
print(f"Total services: {services['total_count']}")
for service in services['services']:
    print(f"  - {service['name']}")
```

---

## JavaScript/Node.js Examples

### Using fetch:

```javascript
// 1. Health check
fetch('http://localhost:8000/api/v1/health')
  .then(response => response.json())
  .then(data => console.log('Health:', data));

// 2. Search for price
fetch('http://localhost:8000/api/v1/search', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    query: 'FedEx 2Day, Zone 5, 3 lb',
    use_cache: true
  })
})
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      console.log(`Price: $${data.price} ${data.currency}`);
      console.log(`Service: ${data.service}`);
    } else {
      console.log(`Error: ${data.error_message}`);
    }
  });

// 3. List services
fetch('http://localhost:8000/api/v1/services')
  .then(response => response.json())
  .then(data => {
    console.log(`Total services: ${data.total_count}`);
    data.services.forEach(service => {
      console.log(`  - ${service.name}`);
    });
  });
```

---

## Testing Workflow

### Complete Test Sequence:

```bash
#!/bin/bash

echo "=== PDF Price Search API Tests ==="
echo

echo "1. Health Check..."
curl -s http://localhost:8000/api/v1/health | python3 -m json.tool
echo

echo "2. Search Test - FedEx 2Day..."
curl -s -X POST 'http://localhost:8000/api/v1/search' \
  -H 'Content-Type: application/json' \
  -d '{"query": "FedEx 2Day, Zone 5, 3 lb"}' | python3 -m json.tool
echo

echo "3. List Services..."
curl -s http://localhost:8000/api/v1/services | python3 -m json.tool
echo

echo "4. Services Summary..."
curl -s http://localhost:8000/api/v1/services/summary | python3 -m json.tool
echo

echo "5. Cache Stats..."
curl -s http://localhost:8000/api/v1/cache/stats | python3 -m json.tool
echo

echo "=== Tests Complete ==="
```

Save as `test_api.sh`, make executable with `chmod +x test_api.sh`, and run with `./test_api.sh`

---

## Performance Testing

### Concurrent Requests Test:

```bash
# Install apache bench if needed: brew install httpd (macOS)

# Test search endpoint with 100 requests, 10 concurrent
ab -n 100 -c 10 -p search_payload.json -T application/json \
  http://localhost:8000/api/v1/search

# Create search_payload.json first:
echo '{"query": "FedEx 2Day, Zone 5, 3 lb"}' > search_payload.json
```

---

## Troubleshooting

### API not responding?
```bash
# Check if API is running
curl http://localhost:8000/api/v1/health

# If not running, start it:
source venv/bin/activate
python main_api.py
```

### Invalid queries?
Make sure your query includes:
- Service name (or variant)
- Zone (2-8)
- Weight (with unit: lb or lbs)

Examples of valid queries:
- "FedEx 2Day, Zone 5, 3 lb"
- "Standard Overnight z2 10 lbs"
- "Express Saver Z8 1 lb"

---

**API Server is running at**: http://localhost:8000
**Interactive Docs**: http://localhost:8000/docs
