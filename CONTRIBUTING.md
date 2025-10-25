# Contributing to PDF Price Search

Thank you for your interest in contributing to PDF Price Search!

## Getting Started

1. Fork the repository
2. Clone your fork
3. Create a feature branch
4. Make your changes
5. Submit a pull request

## Development Setup

```bash
# Clone repository
git clone https://github.com/edubskiy/pdf-price-search.git
cd pdf-price-search

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
make install-dev
```

## Coding Standards

### Python Style

- Follow PEP 8
- Use type hints
- Write docstrings for all public APIs
- Maximum line length: 88 characters (Black default)

### Documentation

- Use Google-style docstrings
- Include examples in docstrings
- Update README.md for new features
- Add tests for all new code

### Testing

- Write unit tests for all new code
- Maintain 85%+ code coverage
- Test edge cases and error conditions
- Use pytest fixtures for test setup

```bash
# Run tests
make test

# Run with coverage
make coverage

# Run specific test file
pytest tests/unit/domain/test_zone.py -v
```

## Pull Request Process

1. **Create a branch**
   ```bash
   git checkout -b feature/my-new-feature
   ```

2. **Make changes**
   - Write code
   - Add tests
   - Update documentation

3. **Run quality checks**
   ```bash
   make qa  # Runs format, lint, type-check, and tests
   ```

4. **Commit changes**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

   Use conventional commits:
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation
   - `test:` Tests
   - `refactor:` Code refactoring
   - `chore:` Maintenance

5. **Push and create PR**
   ```bash
   git push origin feature/my-new-feature
   ```

6. **PR Guidelines**
   - Describe what changed and why
   - Reference related issues
   - Include screenshots if relevant
   - Ensure CI passes

## Code Review

- All PRs require review
- Address review comments
- Keep PR scope focused
- Update PR based on feedback

## Architecture Guidelines

Follow Domain-Driven Design principles:

- **Domain Layer**: Business logic only, no external dependencies
- **Application Layer**: Use cases and orchestration
- **Infrastructure Layer**: External services and implementations
- **Presentation Layer**: API and CLI interfaces

## Testing Guidelines

### Unit Tests

Test individual components in isolation:

```python
def test_zone_validation():
    with pytest.raises(InvalidZoneException):
        Zone(10)  # Invalid zone number
```

### Integration Tests

Test component interactions:

```python
def test_repository_loads_from_pdf():
    repo = PriceRepository(FileCache())
    services = repo.load_from_pdf("test.pdf")
    assert len(services) > 0
```

### E2E Tests

Test complete workflows:

```python
def test_api_search_endpoint(client):
    response = client.post("/api/search", json={"query": "2lb zone 5"})
    assert response.status_code == 200
```

## Documentation

- Update docs/ for architectural changes
- Add examples/ for new features
- Update README.md for user-facing changes
- Include code comments for complex logic

## Questions?

- Open an issue for questions
- Join discussions
- Check existing issues first

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
