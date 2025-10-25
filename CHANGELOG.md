# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-10-25

### Added

- Initial release of PDF Price Search
- Domain-Driven Design architecture with four layers
- Natural language query parsing for shipping prices
- PDF table extraction using pdfplumber
- REST API with FastAPI
- Command-line interface (CLI)
- File-based and in-memory caching
- Comprehensive test suite (unit, integration, e2e, performance)
- Docker support with docker-compose
- Complete documentation (API, CLI, architecture, development)
- Example scripts for common use cases
- Showcase script demonstrating all features

#### Domain Layer

- Value Objects: Zone, Weight, PriceQuery
- Entities: PriceResult
- Aggregates: ShippingService
- Domain Services: QueryParser, ServiceMatcher
- Domain Exceptions: InvalidZoneException, InvalidWeightException, InvalidQueryException

#### Application Layer

- Use Cases: SearchPriceUseCase, ListServicesUseCase, LoadDataUseCase
- Services: PriceSearchService, PDFLoaderService
- DTOs: SearchRequest, SearchResponse, ServiceInfo
- Configuration management with AppConfig
- Dependency injection container

#### Infrastructure Layer

- PDF parsing with pdfplumber
- Table extraction and normalization
- Repository pattern implementation
- File-based cache with JSON serialization
- In-memory price cache with LRU eviction

#### Presentation Layer

- FastAPI REST API with 9 endpoints
- CLI with interactive and command modes
- Input validation
- OpenAPI documentation (Swagger/ReDoc)

#### Testing

- 85%+ code coverage
- Unit tests for all domain, application, and infrastructure components
- Integration tests for workflows
- End-to-end tests for API and CLI
- Performance tests for benchmarking

#### Documentation

- Comprehensive README.md
- Architecture documentation
- API documentation with examples
- CLI documentation
- Deployment guide
- Development guide
- Contributing guidelines
- Example scripts
- Showcase demonstration

### Performance

- Average search time: <100ms (cached)
- PDF loading: <5s per file
- Concurrent request handling: >10 req/s
- Memory efficient: <100MB for typical PDFs

### Supported Features

- Natural language queries: "2lb to zone 5", "FedEx 2Day, 5 pounds, zone 8"
- Multiple service types: FedEx 2Day, Standard Overnight, Ground, etc.
- Zone support: 1-8
- Weight support: 1-150+ lbs
- Currency: USD
- Cache invalidation on file changes
- Batch search operations
- Service discovery and filtering

## [Unreleased]

### Planned

- Database integration (PostgreSQL/MongoDB)
- GraphQL API
- WebSocket support for real-time updates
- Machine learning for improved query parsing
- Multi-currency support
- User authentication and authorization
- Rate limiting
- API versioning
- Distributed caching (Redis)
- Background job processing
- Webhook support
- Export functionality (CSV, Excel)
- Historical price tracking
- Price comparison across services

[1.0.0]: https://github.com/edubskiy/pdf-price-search/releases/tag/v1.0.0
