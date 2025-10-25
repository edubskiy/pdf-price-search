# PDF Price Search

A high-performance system for extracting and searching shipping prices in PDF documents using Domain-Driven Design (DDD) architecture. Search for prices using natural language queries like "2lb to zone 5" or "FedEx 2Day, 5 pounds, zone 8".

## Features

- **Natural Language Queries**: Parse queries like "2lb to zone 5", "5 pounds zone 8", etc.
- **PDF Table Extraction**: Automatically extract price tables from PDF documents
- **Multiple Service Support**: Handle multiple shipping services (FedEx, UPS, USPS, etc.)
- **High Performance**: Sub-100ms search times with intelligent caching
- **RESTful API**: FastAPI-based REST API with OpenAPI documentation
- **CLI Interface**: Command-line interface for terminal usage
- **Domain-Driven Design**: Clean architecture following DDD and SOLID principles
- **Comprehensive Testing**: 85%+ test coverage with unit, integration, and e2e tests
- **Production Ready**: Docker support, health checks, and performance monitoring

## Quick Start

```bash
# Clone and setup
git clone https://github.com/edubskiy/pdf-price-search.git
cd pdf-price-search
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Add your PDF files to the source/ directory
cp your-pricing.pdf source/

# Run the showcase
python showcase/showcase.py

# Or use the CLI
python -m src.presentation.cli search "2lb to zone 5"

# Or start the API server
uvicorn src.presentation.api.main:app --reload
```

## Project Structure

```
pdf-price-search/
├── src/
│   ├── domain/              # Domain layer (business logic)
│   │   ├── entities/        # PriceResult
│   │   ├── value_objects/   # Zone, Weight, PriceQuery
│   │   ├── aggregates/      # ShippingService
│   │   └── services/        # QueryParser, ServiceMatcher
│   ├── application/         # Application layer
│   │   ├── use_cases/       # SearchPriceUseCase, LoadDataUseCase
│   │   ├── services/        # PriceSearchService, PDFLoaderService
│   │   └── dto/            # SearchRequest, SearchResponse
│   ├── infrastructure/      # Infrastructure layer
│   │   ├── pdf/            # PDFParser, TableExtractor, Repository
│   │   └── cache/          # FileCache, PriceCache
│   └── presentation/        # Presentation layer
│       ├── api/            # FastAPI endpoints
│       └── cli.py          # Command-line interface
├── tests/
│   ├── unit/               # Unit tests (domain, application, infrastructure)
│   ├── integration/        # Integration tests (workflows)
│   ├── e2e/               # End-to-end tests (API, CLI)
│   └── performance/        # Performance benchmarks
├── docs/                   # Documentation
│   ├── architecture.md     # Architecture details
│   ├── api_documentation.md
│   ├── cli_documentation.md
│   ├── deployment.md
│   └── development.md
├── examples/               # Example scripts
│   ├── basic_search.py
│   ├── batch_search.py
│   ├── api_client.py
│   └── load_and_search.py
├── showcase/              # Complete demonstration
│   └── showcase.py
└── source/                # PDF files directory
```

## Prerequisites

- Python 3.11 or higher
- pip (Python package installer)

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/edubskiy/pdf-price-search.git
cd pdf-price-search
```

### 2. Create and activate virtual environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install dependencies

```bash
# Install production dependencies
make install

# Or install development dependencies (includes production deps)
make install-dev
```

## Usage

### CLI Examples

```bash
# Basic search
python -m src.presentation.cli search "2lb to zone 5"

# With service filter
python -m src.presentation.cli search "FedEx 2Day, 5lb, zone 8"

# List available services
python -m src.presentation.cli list

# Load PDFs from directory
python -m src.presentation.cli load ./source

# Interactive mode
python -m src.presentation.cli
```

### API Examples

Start the server:
```bash
# Using make
make run

# Or directly with uvicorn
uvicorn src.presentation.api.main:app --reload
```

The API will be available at `http://localhost:8000`

Search for a price:
```bash
curl -X POST "http://localhost:8000/api/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "2lb to zone 5"}'
```

Response:
```json
{
  "success": true,
  "price": 18.25,
  "currency": "USD",
  "service": "FedEx Ground",
  "zone": 5,
  "weight": 2.0,
  "source_document": "fedex_rates.pdf",
  "search_time_ms": 12.3
}
```

### API Documentation

Interactive API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Python Code Examples

```python
from src.application.container import Container
from src.application.use_cases.search_price_use_case import SearchPriceUseCase
from src.application.use_cases.load_data_use_case import LoadDataUseCase
from src.application.dto.search_request import SearchRequest

# Initialize
container = Container()

# Load PDFs
load_use_case = LoadDataUseCase(container)
result = load_use_case.execute_from_directory("./source")

# Search for price
search_use_case = SearchPriceUseCase(container)
request = SearchRequest(query="2lb to zone 5")
response = search_use_case.execute(request)

if response.success:
    print(f"Price: ${response.price} {response.currency}")
    print(f"Service: {response.service}")
```

See more examples in the `examples/` directory.

## Testing

The project maintains **85%+ test coverage** across all layers.

### Running Tests

```bash
# Run all tests with coverage
make coverage

# Run specific test types
make test-unit         # Unit tests only
make test-integration  # Integration tests only
make test-e2e         # End-to-end tests only

# Run performance tests
pytest tests/performance/ -v -s

# Run specific test file
pytest tests/unit/domain/test_zone.py -v
```

### Test Organization

- **Unit Tests** (`tests/unit/`): Test individual components in isolation
- **Integration Tests** (`tests/integration/`): Test component interactions
- **E2E Tests** (`tests/e2e/`): Test complete user workflows
- **Performance Tests** (`tests/performance/`): Benchmark system performance

### Code Quality

```bash
# Format code
make format

# Lint code
make lint

# Type check
make type-check

# Run all quality checks
make qa
```

## Performance

Performance metrics from real-world testing:

- **Search Speed**: <100ms (cached), <500ms (cold)
- **PDF Loading**: <5s per file
- **Throughput**: >10 requests/second
- **Memory Usage**: <100MB for typical PDFs
- **Cache Hit Rate**: >85% in normal usage

## Docker

### Build and Run

```bash
# Build image
docker build -t pdf-price-search .

# Run container
docker run -p 8000:8000 -v $(pwd)/source:/app/source pdf-price-search

# Using docker-compose
docker-compose up -d
```

## Configuration

Configuration via environment variables or `.env` file:

```bash
# PDF Settings
PDF_SEARCH_DIR=./source          # Default PDF directory
PDF_SEARCH_MAX_SIZE_MB=50        # Max PDF file size

# Cache Settings
PDF_SEARCH_CACHE_DIR=./.cache    # Cache directory
PDF_SEARCH_ENABLE_CACHE=true     # Enable caching

# Logging
PDF_SEARCH_LOG_LEVEL=INFO        # Log level (DEBUG, INFO, WARNING, ERROR)
```

## Architecture

This project follows **Domain-Driven Design (DDD)** with a clean, layered architecture:

```
┌─────────────────────────────────────┐
│    Presentation Layer (API/CLI)     │  ← User Interface
├─────────────────────────────────────┤
│    Application Layer (Use Cases)    │  ← Business Workflows
├─────────────────────────────────────┤
│    Domain Layer (Business Logic)    │  ← Core Logic
├─────────────────────────────────────┤
│  Infrastructure Layer (External)    │  ← PDF, Cache, etc.
└─────────────────────────────────────┘
```

### Domain Layer (Pure Business Logic)

- **Value Objects**: `Zone`, `Weight`, `PriceQuery` - Immutable, value-based
- **Entities**: `PriceResult` - Identity-based, mutable
- **Aggregates**: `ShippingService` - Cluster of entities with root
- **Domain Services**: `QueryParser`, `ServiceMatcher` - Business logic

### Application Layer (Orchestration)

- **Use Cases**: `SearchPriceUseCase`, `LoadDataUseCase` - Business workflows
- **Services**: `PriceSearchService`, `PDFLoaderService` - Coordination
- **DTOs**: `SearchRequest`, `SearchResponse` - Data transfer
- **Container**: Dependency injection and lifecycle management

### Infrastructure Layer (Technical Capabilities)

- **PDF Processing**: `PDFParser`, `TableExtractor` - Extract data from PDFs
- **Repository**: `PriceRepository` - Data access abstraction
- **Caching**: `FileCache`, `PriceCache` - Performance optimization

### Presentation Layer (User Interface)

- **API**: FastAPI REST endpoints with OpenAPI docs
- **CLI**: Command-line interface with interactive mode
- **Validation**: Input validation and sanitization

### Design Patterns

- **Repository Pattern**: Abstract data access
- **Factory Pattern**: Complex object creation
- **Dependency Injection**: Manage dependencies
- **Strategy Pattern**: Algorithm encapsulation
- **Value Object Pattern**: Immutable domain concepts

### SOLID Principles

- **Single Responsibility**: Each class has one reason to change
- **Open/Closed**: Open for extension, closed for modification
- **Liskov Substitution**: Subtypes are substitutable
- **Interface Segregation**: Specific interfaces over general ones
- **Dependency Inversion**: Depend on abstractions

See [docs/architecture.md](docs/architecture.md) for detailed architecture documentation.

## Documentation

- [Architecture Guide](docs/architecture.md) - Detailed architecture explanation
- [API Documentation](docs/api_documentation.md) - Complete API reference
- [CLI Documentation](docs/cli_documentation.md) - CLI command reference
- [Deployment Guide](docs/deployment.md) - Deployment instructions
- [Development Guide](docs/development.md) - Development workflow

## Examples

Check the `examples/` directory for complete examples:

- `basic_search.py` - Simple search example
- `batch_search.py` - Batch processing example
- `api_client.py` - API client example
- `load_and_search.py` - Complete workflow example

Run the showcase to see all features:
```bash
python showcase/showcase.py
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and add tests
4. Run quality checks (`make qa`)
5. Commit your changes (`git commit -m 'feat: add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and changes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- PDF parsing with [pdfplumber](https://github.com/jsvine/pdfplumber)
- Testing with [pytest](https://pytest.org/)

## Support

- GitHub Issues: [Report bugs](https://github.com/edubskiy/pdf-price-search/issues)
- GitHub Discussions: [Ask questions](https://github.com/edubskiy/pdf-price-search/discussions)

## Author

Evgeniy Dubskiy

---

Made with ❤️ using Domain-Driven Design principles
