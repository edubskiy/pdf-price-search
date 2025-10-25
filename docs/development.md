# Development Guide

## Setup

### 1. Clone Repository

```bash
git clone https://github.com/edubskiy/pdf-price-search.git
cd pdf-price-search
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
make install-dev
```

## Development Workflow

### Running Tests

```bash
# All tests
make test

# Unit tests only
make test-unit

# Integration tests
make test-integration

# With coverage
make coverage
```

### Code Quality

```bash
# Format code
make format

# Lint
make lint

# Type check
make type-check

# All checks
make qa
```

### Running the Application

```bash
# API server
make run

# CLI
python -m src.presentation.cli
```

## Project Structure

Follow DDD principles:
- `domain/` - Business logic (no external dependencies)
- `application/` - Use cases and orchestration
- `infrastructure/` - External services and implementations
- `presentation/` - API and CLI interfaces

## Testing Guidelines

1. **Unit tests** - Test components in isolation
2. **Integration tests** - Test component interactions
3. **E2E tests** - Test complete workflows
4. **Performance tests** - Test system performance

### Writing Tests

```python
# Unit test example
def test_zone_validation():
    with pytest.raises(InvalidZoneException):
        Zone(10)

# Integration test example
def test_repository_search():
    repo = PriceRepository(FileCache())
    results = repo.search_price(query)
    assert len(results) > 0
```

## Coding Standards

### Naming Conventions

- Classes: `PascalCase`
- Functions: `snake_case`
- Constants: `UPPER_CASE`
- Private: `_leading_underscore`

### Documentation

- All public APIs must have docstrings
- Use Google-style docstrings
- Include type hints

```python
def search_price(query: PriceQuery) -> List[PriceResult]:
    """
    Search for shipping prices.

    Args:
        query: The price query to search for.

    Returns:
        List of matching price results.

    Raises:
        InvalidQueryException: If query is invalid.
    """
    pass
```

## Git Workflow

### Branching

- `main` - Production-ready code
- `develop` - Development branch
- `feature/*` - Feature branches
- `bugfix/*` - Bug fix branches

### Commits

Follow conventional commits:
```
feat: add new feature
fix: bug fix
docs: documentation
test: add tests
refactor: code refactoring
```

### Pull Requests

1. Create feature branch
2. Make changes and add tests
3. Run QA checks
4. Submit PR with description
5. Address review comments
6. Merge after approval

## Debugging

### Logging

```python
import logging

logger = logging.getLogger(__name__)
logger.debug("Debug message")
logger.info("Info message")
logger.error("Error message")
```

### Debugging Tools

- `pdb` - Python debugger
- `pytest --pdb` - Debug failed tests
- IDE debugger (VSCode, PyCharm)

## Performance Optimization

1. **Profile code** - Use `cProfile`
2. **Optimize queries** - Cache results
3. **Async operations** - Use `asyncio` where appropriate
4. **Batch processing** - Process multiple items at once

## Contributing

See CONTRIBUTING.md for detailed guidelines.
