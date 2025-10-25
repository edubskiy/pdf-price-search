# PDF Price Search Implementation Plan

## Executive Summary

This document outlines the implementation plan for a PDF-based price search tool that extracts shipping rates from FedEx PDF documents based on free-form text queries.

## Requirements Summary

### Core Functionality
- **Input**: Single free-form text line (e.g., "FedEx 2Day, Zone 5, 3 lb")
- **Output**: Base list rate in USD
- **Data Source**: PDF price tables (FedEx Standard List Rates, PriceAnnex)
- **Scalability**: Process different PDF documents without code changes

### Technical Requirements
- Domain-Driven Design (DDD) architecture
- SOLID principles adherence
- Simplicity over complexity
- Minimum 85% test coverage
- Documentation after implementation

### Delivery Timeline
3-6 hours for core implementation

## Architecture Design (DDD)

### Layered Architecture

```
┌─────────────────────────────────────────────────┐
│           Presentation Layer                     │
│   • CLI Interface                               │
│   • HTTP API Endpoint                           │
└─────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────┐
│           Application Layer                      │
│   • Price Search Service                        │
│   • Query Parser Service                        │
└─────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────┐
│           Domain Layer                           │
│   • Price Query (Value Object)                  │
│   • Price Result (Entity)                       │
│   • Shipping Service (Aggregate)                │
│   • Zone (Value Object)                         │
│   • Weight (Value Object)                       │
└─────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────┐
│           Infrastructure Layer                   │
│   • PDF Repository                              │
│   • PDF Parser Adapter                          │
│   • Price Data Cache                            │
└─────────────────────────────────────────────────┘
```

## Domain Model

### Core Entities and Value Objects

1. **PriceQuery** (Value Object)
   - service_type: str (e.g., "FedEx 2Day", "Standard Overnight")
   - zone: Zone
   - weight: Weight
   - packaging_type: Optional[str]

2. **Zone** (Value Object)
   - value: int (1-8)
   - Handles normalization ("z2", "Zone 5", "zone 3")

3. **Weight** (Value Object)
   - value: float
   - unit: str (lb, lbs)
   - Handles parsing ("3 lb", "10 lbs")

4. **PriceResult** (Entity)
   - price: Decimal
   - currency: str = "USD"
   - service_type: str
   - zone: Zone
   - weight: Weight
   - source_document: str

5. **ShippingService** (Aggregate Root)
   - service_name: str
   - price_table: Dict
   - get_price(zone: Zone, weight: Weight) -> Decimal

### Domain Services

1. **QueryParser** (Domain Service)
   - parse(query: str) -> PriceQuery
   - Handles free-form text parsing

2. **PriceSearchService** (Domain Service)
   - search(query: PriceQuery) -> PriceResult
   - Orchestrates the search process

## Implementation Phases

### Phase 1: Infrastructure Setup (30 minutes)
- [ ] Project structure setup
- [ ] Virtual environment and dependencies
- [ ] Basic directory structure following DDD

### Phase 2: Domain Layer (1 hour)
- [ ] Implement Value Objects (Zone, Weight)
- [ ] Implement PriceQuery and PriceResult
- [ ] Implement QueryParser service
- [ ] Unit tests for domain objects

### Phase 3: Infrastructure Layer (1.5 hours)
- [ ] PDF parser implementation using pdfplumber
- [ ] Data extraction and structuring
- [ ] Price table repository
- [ ] Caching mechanism for parsed data
- [ ] Unit tests for parsers

### Phase 4: Application Layer (1 hour)
- [ ] PriceSearchService implementation
- [ ] Query orchestration
- [ ] Error handling
- [ ] Integration tests

### Phase 5: Presentation Layer (1 hour)
- [ ] CLI interface implementation
- [ ] HTTP API endpoint (FastAPI)
- [ ] Input validation
- [ ] Response formatting
- [ ] End-to-end tests

### Phase 6: Documentation & Testing (30 minutes)
- [ ] README documentation
- [ ] API documentation
- [ ] Ensure 85% test coverage
- [ ] Performance testing

## Technology Stack

### Core Dependencies
```python
# Production
pdfplumber>=0.11.0      # PDF parsing
fastapi>=0.104.0        # HTTP API
uvicorn>=0.24.0         # ASGI server
pydantic>=2.0.0         # Data validation
python-multipart>=0.0.6 # Form data handling

# Development
pytest>=7.4.0           # Testing framework
pytest-cov>=4.1.0       # Coverage reporting
black>=23.0.0           # Code formatting
mypy>=1.5.0             # Type checking
```

### Project Structure
```
pdf-price-search/
├── src/
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── entities/
│   │   │   ├── __init__.py
│   │   │   └── price_result.py
│   │   ├── value_objects/
│   │   │   ├── __init__.py
│   │   │   ├── zone.py
│   │   │   ├── weight.py
│   │   │   └── price_query.py
│   │   ├── aggregates/
│   │   │   ├── __init__.py
│   │   │   └── shipping_service.py
│   │   └── services/
│   │       ├── __init__.py
│   │       └── query_parser.py
│   ├── application/
│   │   ├── __init__.py
│   │   └── price_search_service.py
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   ├── pdf/
│   │   │   ├── __init__.py
│   │   │   ├── parser.py
│   │   │   └── repository.py
│   │   └── cache/
│   │       ├── __init__.py
│   │       └── price_cache.py
│   └── presentation/
│       ├── __init__.py
│       ├── cli.py
│       └── api/
│           ├── __init__.py
│           ├── main.py
│           └── endpoints.py
├── tests/
│   ├── unit/
│   │   ├── domain/
│   │   ├── application/
│   │   └── infrastructure/
│   ├── integration/
│   └── e2e/
├── source/              # PDF files
├── docs/
├── requirements.txt
├── requirements-dev.txt
├── pytest.ini
├── .gitignore
└── README.md
```

## Implementation Details

### PDF Parsing Strategy
1. Use pdfplumber to extract tables from PDFs
2. Identify table structure (headers, zones, weights, prices)
3. Create structured data mapping: `{service_type: {zone: {weight: price}}}`
4. Cache parsed data for performance

### Query Parsing Algorithm
1. Tokenize input string
2. Identify service type keywords
3. Extract zone information (handle variations: "z2", "Zone 5")
4. Extract weight information (handle "lb", "lbs")
5. Handle optional packaging type
6. Validate extracted components

### Price Lookup Process
1. Parse user query into PriceQuery object
2. Load/cache PDF data
3. Match service type to available services
4. Find price based on zone and weight
5. Return formatted PriceResult

## Testing Strategy

### Unit Tests (Target: 40% of tests)
- Domain objects validation
- Query parser edge cases
- Weight/Zone normalization

### Integration Tests (Target: 30% of tests)
- PDF parsing accuracy
- Cache functionality
- Repository operations

### End-to-End Tests (Target: 30% of tests)
- Complete query flow
- API endpoint testing
- CLI interface testing

### Test Cases Examples
```python
# Query variations to test
test_queries = [
    "FedEx 2Day, Zone 5, 3 lb",
    "Standard Overnight, z2, 10 lbs, other packaging",
    "Express Saver Z8 1 lb",
    "Ground Z6 12 lb",
    "Home Delivery zone 3 5 lb"
]
```

## Error Handling

1. **Invalid Query Format**: Return clear error message with expected format
2. **Service Not Found**: Suggest available services
3. **Zone Out of Range**: Indicate valid zone range
4. **Weight Not Found**: Return closest available weights
5. **PDF Parse Error**: Fallback to cached data or clear error

## Performance Considerations

1. **Caching**: Parse PDFs once and cache structured data
2. **Lazy Loading**: Load PDF data only when needed
3. **Index Creation**: Create lookup indexes for fast searches
4. **Memory Management**: Stream large PDFs instead of loading entirely

## SOLID Principles Application

### Single Responsibility
- Each class has one reason to change
- QueryParser only parses queries
- PdfRepository only handles PDF operations

### Open/Closed
- New PDF formats can be added via new parser implementations
- New service types extend base ShippingService

### Liskov Substitution
- All value objects are immutable and substitutable
- Parser implementations follow common interface

### Interface Segregation
- Separate interfaces for parsing, searching, and caching
- Clients depend only on methods they use

### Dependency Inversion
- Domain doesn't depend on infrastructure
- Use dependency injection for repositories and services

## Questions for Clarification

1. **Service Type Matching**: Should we use fuzzy matching for service names (e.g., "2Day" vs "2-Day")?
2. **Weight Interpolation**: If exact weight not found, should we interpolate or return next highest?
3. **Multiple Results**: If query matches multiple services, return all or best match?
4. **PDF Updates**: How often are PDFs updated? Need automatic refresh mechanism?
5. **Performance Requirements**: Expected query volume and response time targets?

## Deliverables Checklist

- [ ] Source code with DDD architecture
- [ ] CLI interface
- [ ] HTTP API endpoint
- [ ] 85%+ test coverage
- [ ] README with setup and usage instructions
- [ ] Architecture documentation
- [ ] Demo preparation

## Next Steps

Upon approval of this plan:
1. Set up project structure and dependencies
2. Implement domain layer with tests
3. Build infrastructure for PDF parsing
4. Create application services
5. Develop presentation interfaces
6. Complete documentation
7. Prepare demo

---

**Estimated Total Time**: 5-6 hours
**Risk Buffer**: 1 hour for unforeseen complexities