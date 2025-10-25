# Architecture Documentation

## Overview

The PDF Price Search system is built using **Domain-Driven Design (DDD)** principles and follows a clean, layered architecture. This document explains the architectural decisions, layer responsibilities, and design patterns used throughout the system.

## Table of Contents

1. [Architecture Layers](#architecture-layers)
2. [Domain Layer](#domain-layer)
3. [Application Layer](#application-layer)
4. [Infrastructure Layer](#infrastructure-layer)
5. [Presentation Layer](#presentation-layer)
6. [Design Patterns](#design-patterns)
7. [Data Flow](#data-flow)
8. [Dependency Management](#dependency-management)

## Architecture Layers

The system is organized into four distinct layers, each with specific responsibilities:

```
┌─────────────────────────────────────────────┐
│         Presentation Layer                   │
│  (CLI, API Controllers, Request Validation)  │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│         Application Layer                    │
│  (Use Cases, DTOs, Services, Config)         │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│         Domain Layer                         │
│  (Entities, Value Objects, Domain Services)  │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│         Infrastructure Layer                 │
│  (PDF Parsing, Caching, External Services)   │
└─────────────────────────────────────────────┘
```

### Layer Dependency Rules

- **Presentation** depends on **Application**
- **Application** depends on **Domain**
- **Infrastructure** depends on **Domain**
- **Domain** depends on nothing (pure business logic)

This ensures the business logic (Domain) remains independent of external concerns.

## Domain Layer

The Domain Layer contains the core business logic and domain models. It has no dependencies on other layers.

### Components

#### 1. Entities

Entities have identity and lifecycle. They are mutable and distinguished by their unique ID.

- **PriceResult** (`domain/entities/price_result.py`)
  - Represents a shipping price lookup result
  - Has unique ID (UUID)
  - Contains price, service type, zone, weight, and metadata
  - Equality based on ID, not value

```python
price_result = PriceResult(
    price=Decimal("25.50"),
    service_type="FedEx 2Day",
    zone=Zone(5),
    weight=Weight(3),
    source_document="fedex_rates.pdf"
)
```

#### 2. Value Objects

Value objects are immutable and defined by their values, not identity.

- **Zone** (`domain/value_objects/zone.py`)
  - Represents a shipping zone (1-8)
  - Immutable
  - Validates zone number
  - Equality based on value

- **Weight** (`domain/value_objects/weight.py`)
  - Represents package weight in pounds
  - Immutable
  - Validates weight > 0
  - Supports comparison operations

- **PriceQuery** (`domain/value_objects/price_query.py`)
  - Represents a price search query
  - Contains weight and zone
  - Immutable and validated

```python
zone = Zone(5)
weight = Weight(3)
query = PriceQuery(weight=weight, zone=zone)
```

#### 3. Aggregates

Aggregates are clusters of entities and value objects treated as a single unit.

- **ShippingService** (`domain/aggregates/shipping_service.py`)
  - Root entity for a shipping service
  - Contains service name and price table
  - Enforces invariants (e.g., price table consistency)
  - Entry point for all operations on the aggregate

```python
service = ShippingService(
    name="FedEx 2Day",
    source_document="fedex_rates.pdf",
    price_table=price_table
)
```

#### 4. Domain Services

Domain services encapsulate business logic that doesn't naturally belong to an entity or value object.

- **QueryParser** (`domain/services/query_parser.py`)
  - Parses natural language queries
  - Extracts weight and zone information
  - Business logic for query interpretation

- **ServiceMatcher** (`domain/services/service_matcher.py`)
  - Matches queries to shipping services
  - Implements fuzzy matching logic
  - Returns best matching services

```python
query = query_parser.parse("2lb to zone 5")
matches = service_matcher.find_matches(services, "FedEx")
```

#### 5. Domain Exceptions

- **DomainException** - Base exception for all domain errors
- **InvalidZoneException** - Invalid zone number
- **InvalidWeightException** - Invalid weight value
- **InvalidQueryException** - Invalid query format

## Application Layer

The Application Layer orchestrates the domain logic and coordinates between layers.

### Components

#### 1. Use Cases

Use cases represent application-specific business logic and workflows.

- **SearchPriceUseCase** - Search for shipping prices
- **ListServicesUseCase** - List available shipping services
- **LoadDataUseCase** - Load PDF data into the system

Each use case:
- Has a single responsibility
- Is independent and reusable
- Returns DTOs (not domain objects)
- Handles application-level errors

```python
search_use_case = SearchPriceUseCase(container)
response = search_use_case.execute(SearchRequest(query="2lb to zone 5"))
```

#### 2. Services

Application services coordinate complex operations.

- **PriceSearchService** - Orchestrates price searches
- **PDFLoaderService** - Manages PDF loading

#### 3. DTOs (Data Transfer Objects)

DTOs transfer data between layers without exposing domain internals.

- **SearchRequest** - Input for price search
- **SearchResponse** - Output from price search
- **ServiceInfo** - Information about a shipping service

```python
request = SearchRequest(
    query="2lb to zone 5",
    service_filter=None,
    limit=10
)

response = SearchResponse(
    query=request.query,
    results=[...],
    total_results=5,
    search_time_ms=15.2
)
```

#### 4. Configuration

- **AppConfig** - Application configuration management
  - PDF directory paths
  - Cache settings
  - Performance limits

#### 5. Container

- **Container** - Dependency injection container
  - Manages object lifecycle
  - Resolves dependencies
  - Provides singleton instances

```python
container = Container()
repository = container.get_repository()
cache = container.get_cache()
```

## Infrastructure Layer

The Infrastructure Layer provides technical capabilities and external integrations.

### Components

#### 1. PDF Processing

- **PDFParser** (`infrastructure/pdf/pdf_parser.py`)
  - Parses PDF files using pdfplumber
  - Extracts tables and text
  - Handles various PDF formats

- **TableExtractor** (`infrastructure/pdf/table_extractor.py`)
  - Extracts structured tables from PDFs
  - Normalizes table data
  - Handles merged cells and formatting

- **ServiceFactory** (`infrastructure/pdf/service_factory.py`)
  - Creates ShippingService aggregates from parsed data
  - Maps PDF data to domain models
  - Validates and transforms data

- **PriceRepository** (`infrastructure/pdf/repository.py`)
  - Implements repository pattern
  - Loads and stores shipping services
  - Provides query interface
  - Uses caching for performance

```python
repository = PriceRepository(file_cache)
services = repository.load_from_pdf("fedex_rates.pdf")
results = repository.search_price(query, service_filter)
```

#### 2. Caching

- **FileCache** (`infrastructure/cache/file_cache.py`)
  - File-based caching with JSON serialization
  - Persistent across restarts
  - Key-based storage
  - Automatic cache invalidation on file changes

- **PriceCache** (`infrastructure/cache/price_cache.py`)
  - In-memory caching for price lookups
  - LRU eviction policy
  - Fast repeated queries

```python
cache = FileCache(".cache")
cache.set("key", data)
cached_data = cache.get("key")
```

## Presentation Layer

The Presentation Layer handles user interaction and external communication.

### Components

#### 1. API (FastAPI)

- **Endpoints** (`presentation/api/endpoints.py`)
  - RESTful API endpoints
  - Request/response handling
  - HTTP status codes

- **Models** (`presentation/api/models.py`)
  - Pydantic models for request/response validation
  - OpenAPI documentation

- **Dependencies** (`presentation/api/dependencies.py`)
  - FastAPI dependency injection
  - Container initialization

```python
@router.post("/search", response_model=SearchResponseModel)
async def search_prices(
    request: SearchRequestModel,
    use_case: SearchPriceUseCase = Depends(get_search_use_case)
):
    return use_case.execute(request.to_dto())
```

#### 2. CLI

- **CLI** (`presentation/cli.py`)
  - Command-line interface
  - Interactive prompts
  - Formatted output

```bash
python -m src.presentation.cli search "2lb to zone 5"
```

#### 3. Validation

- **InputValidator** (`presentation/validation/input_validator.py`)
  - Validates user input
  - Sanitizes data
  - Returns user-friendly error messages

## Design Patterns

### 1. Repository Pattern

Abstracts data access and provides a collection-like interface.

```python
class PriceRepositoryInterface(ABC):
    @abstractmethod
    def load_from_pdf(self, pdf_path: str) -> List[ShippingService]:
        pass

    @abstractmethod
    def search_price(self, query: PriceQuery, service_filter: Optional[str]) -> List[PriceResult]:
        pass
```

### 2. Factory Pattern

Creates complex objects with validation and transformation.

```python
class ServiceFactory:
    def create_service(self, name: str, data: dict) -> ShippingService:
        # Complex creation logic
        pass
```

### 3. Dependency Injection

Manages dependencies and promotes testability.

```python
class SearchPriceUseCase:
    def __init__(self, container: Container):
        self.repository = container.get_repository()
        self.cache = container.get_cache()
```

### 4. Strategy Pattern

Encapsulates algorithms (e.g., different query parsing strategies).

```python
class QueryParser:
    def parse(self, query: str) -> PriceQuery:
        # Multiple parsing strategies
        pass
```

### 5. Value Object Pattern

Represents concepts through their values, not identity.

```python
zone1 = Zone(5)
zone2 = Zone(5)
assert zone1 == zone2  # Equal by value
```

## Data Flow

### Search Price Flow

```
1. User Input
   ↓
2. Presentation Layer (API/CLI)
   - Validates input
   - Creates SearchRequest DTO
   ↓
3. Application Layer (Use Case)
   - Parses query
   - Coordinates search
   ↓
4. Domain Layer (Services)
   - Query parsing logic
   - Service matching logic
   ↓
5. Infrastructure Layer (Repository)
   - Loads data (with caching)
   - Executes search
   ↓
6. Domain Layer (Entities)
   - Creates PriceResult entities
   ↓
7. Application Layer
   - Converts to DTOs
   - Creates SearchResponse
   ↓
8. Presentation Layer
   - Formats response
   - Returns to user
```

### PDF Loading Flow

```
1. User provides PDF path
   ↓
2. Application Layer (PDFLoaderService)
   - Validates file
   - Checks cache
   ↓
3. Infrastructure Layer (PDFParser)
   - Extracts tables
   - Parses data
   ↓
4. Infrastructure Layer (ServiceFactory)
   - Creates domain objects
   - Validates data
   ↓
5. Domain Layer (ShippingService)
   - Business validation
   - Enforces invariants
   ↓
6. Infrastructure Layer (Repository)
   - Stores services
   - Updates cache
```

## Dependency Management

### Dependency Inversion Principle

High-level modules depend on abstractions, not concretions.

```python
# Good - Depends on interface
class SearchPriceUseCase:
    def __init__(self, repository: PriceRepositoryInterface):
        self.repository = repository

# Bad - Depends on concrete implementation
class SearchPriceUseCase:
    def __init__(self, repository: PriceRepository):
        self.repository = repository
```

### Container Pattern

The Container manages object creation and lifecycle.

```python
container = Container()
# All dependencies resolved automatically
search_use_case = SearchPriceUseCase(container)
```

## Testing Strategy

### Unit Tests

Test individual components in isolation.

- Mock dependencies
- Test business logic
- Fast execution

```python
def test_zone_validation():
    with pytest.raises(InvalidZoneException):
        Zone(10)  # Invalid zone
```

### Integration Tests

Test component interaction.

- Test real implementations
- Verify data flow
- Database/file operations

```python
def test_repository_search():
    repo = PriceRepository(FileCache())
    repo.load_from_pdf("test.pdf")
    results = repo.search_price(query)
    assert len(results) > 0
```

### End-to-End Tests

Test complete user workflows.

- Test entire system
- Verify API/CLI
- Real PDFs and queries

```python
def test_api_search_endpoint():
    response = client.post("/api/search", json={"query": "2lb to zone 5"})
    assert response.status_code == 200
```

### Performance Tests

Test system performance and scalability.

- Measure response times
- Test concurrent requests
- Memory usage
- Cache effectiveness

## Best Practices

### 1. Domain Logic in Domain Layer

All business rules belong in the domain layer.

```python
# Good - Domain logic in domain
class Weight:
    def __init__(self, pounds: float):
        if pounds <= 0:
            raise InvalidWeightException("Weight must be positive")

# Bad - Domain logic in application
class PDFLoaderService:
    def load(self, weight: float):
        if weight <= 0:  # Domain validation in application layer!
            raise ValueError()
```

### 2. DTOs for Layer Communication

Never expose domain objects directly to external layers.

```python
# Good - Return DTO
def execute(self) -> SearchResponse:
    results = self.repository.search(query)
    return SearchResponse.from_domain(results)

# Bad - Return domain object
def execute(self) -> List[PriceResult]:
    return self.repository.search(query)
```

### 3. Immutable Value Objects

Value objects should be immutable.

```python
# Good - Immutable
class Zone:
    def __init__(self, number: int):
        self._number = number  # Private, immutable

    @property
    def number(self) -> int:
        return self._number

# Bad - Mutable
class Zone:
    def __init__(self, number: int):
        self.number = number  # Can be changed!
```

### 4. Single Responsibility

Each class has one reason to change.

```python
# Good - Single responsibility
class QueryParser:  # Only parses queries
    def parse(self, query: str) -> PriceQuery:
        pass

class PriceSearchService:  # Only coordinates search
    def search(self, query: PriceQuery) -> List[PriceResult]:
        pass

# Bad - Multiple responsibilities
class SearchService:  # Does too much!
    def parse_and_search(self, query: str) -> List[PriceResult]:
        parsed = self.parse(query)
        results = self.search(parsed)
        return results
```

## Future Enhancements

### Planned Improvements

1. **Event Sourcing** - Track all changes as events
2. **CQRS** - Separate read and write models
3. **Microservices** - Split into smaller services
4. **GraphQL API** - Flexible query interface
5. **Machine Learning** - Improve query parsing
6. **Real-time Updates** - WebSocket support

### Scalability Considerations

- **Horizontal Scaling** - Stateless design allows multiple instances
- **Caching Strategy** - Multi-level caching (memory, disk, distributed)
- **Async Processing** - Background PDF processing
- **Database** - Move from file-based to database
- **Message Queue** - Decouple operations

## Conclusion

This architecture provides:

- **Maintainability** - Clear separation of concerns
- **Testability** - Easy to test in isolation
- **Flexibility** - Easy to extend and modify
- **Scalability** - Can handle growth
- **Domain Focus** - Business logic is central and protected

The DDD approach ensures the system accurately models the business domain while remaining flexible for future changes.
