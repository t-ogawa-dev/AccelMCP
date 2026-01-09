# AccelMCP Test Suite

## Overview

Comprehensive test suite for AccelMCP covering unit tests, integration tests, and end-to-end tests.

## Test Structure

```
tests/
├── TEST_COVERAGE.txt          # Detailed test coverage report
├── conftest.py                 # Pytest fixtures and configuration
├── conftest_playwright.py      # Playwright E2E test configuration
│
├── test_models.py              # Database model tests
├── test_api.py                 # API endpoint tests
├── test_views.py               # View/template tests
├── test_mcp_controller.py      # MCP protocol tests
├── test_integration.py         # Integration tests
│
├── test_security.py            # Security feature tests (NEW)
├── test_variables.py           # Variables feature tests (NEW)
├── test_mcp_services.py        # MCP Services tests (NEW)
├── test_admin_settings.py      # Admin settings tests (NEW)
│
└── e2e/                        # End-to-end tests
    ├── test_login.py
    ├── test_dashboard.py
    ├── accounts/
    ├── capabilities/
    ├── mcp_templates/
    └── services/
```

## Running Tests

### All Tests

```bash
pytest tests/
```

### Unit Tests Only

```bash
pytest tests/test_*.py
```

### E2E Tests Only

```bash
pytest tests/e2e/
```

### Specific Test File

```bash
pytest tests/test_security.py
pytest tests/test_variables.py
pytest tests/test_mcp_services.py
```

### With Coverage

```bash
pytest --cov=app --cov-report=html tests/
```

### Verbose Output

```bash
pytest -v tests/
```

### Run Specific Test

```bash
pytest tests/test_security.py::TestBruteForceProtection::test_multiple_failed_logins_trigger_lock
```

## New Test Files

### test_security.py

Tests for security features including:

- Brute-force protection
- IP locking/unlocking
- Login failure tracking
- Lock expiration
- Admin login logs
- Admin action logs (audit trail)
- Security API endpoints

### test_variables.py

Tests for Variables feature including:

- Variable CRUD operations
- Secret variables
- Environment variable references
- Variable replacement in URLs/headers
- Multiple variable replacement
- Missing variable handling

### test_mcp_services.py

Tests for MCP Services feature including:

- MCP Service CRUD operations
- Subdomain vs path routing
- Access control (public/restricted)
- Apps association with MCP Services
- Toggle enabled/disabled state

### test_admin_settings.py

Tests for AdminSettings feature including:

- Settings CRUD operations
- Security settings (max_attempts, lock_duration, audit_retention)
- Language settings
- Settings integration with other features

## Test Coverage

See `TEST_COVERAGE.txt` for detailed coverage report.

### Current Coverage by Module

- **Models**: ~85% (includes new models: Variable, AdminSettings, LoginLockStatus, AdminLoginLog, AdminActionLog, McpService)
- **API Controllers**: ~80% (includes new endpoints for variables, mcp-services, security)
- **Views**: ~80%
- **MCP Protocol**: ~90%
- **E2E**: ~85%
- **Auth & Security**: ~90% (significantly improved)

## Fixtures

### Common Fixtures (conftest.py)

- `app`: Flask application instance
- `client`: Test client for HTTP requests
- `auth_client`: Authenticated test client
- `db`: Database session
- `sample_service`: Test service instance
- `sample_capability`: Test capability instance
- `sample_account`: Test account instance
- `sample_template`: Test template instance

### E2E Fixtures (conftest_playwright.py)

- `page`: Playwright page instance
- `authenticated_page`: Logged-in page instance
- `base_url`: Application base URL

## Writing New Tests

### Unit Test Example

```python
def test_create_variable(self, auth_client):
    """Test POST /api/variables"""
    payload = {
        'name': 'TEST_VAR',
        'value': 'test_value',
        'source_type': 'manual',
        'value_type': 'string',
        'is_secret': False
    }
    response = auth_client.post('/api/variables',
                               data=json.dumps(payload),
                               content_type='application/json')

    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['name'] == 'TEST_VAR'
```

### E2E Test Example

```python
def test_create_variable(self, page: Page):
    """Test creating a variable through UI"""
    page.goto(f"{base_url}/variables/new")
    page.fill("#name", "TEST_VAR")
    page.fill("#value", "test_value")
    page.click("button[type=submit]")

    expect(page.locator(".success-message")).to_be_visible()
```

## Best Practices

1. **Use descriptive test names**: Test names should clearly describe what is being tested
2. **One assertion per test**: Focus each test on a single behavior
3. **Use fixtures**: Leverage pytest fixtures for common setup
4. **Clean up after tests**: Ensure database is clean between tests
5. **Test edge cases**: Include tests for error conditions and edge cases
6. **Mock external services**: Don't make real API calls in tests
7. **Keep tests fast**: Unit tests should run in milliseconds

## Troubleshooting

### Database Issues

```bash
# Reset test database
docker compose exec db mysql -uroot -prootpassword -e "DROP DATABASE IF EXISTS test_mcpdb; CREATE DATABASE test_mcpdb;"
```

### Playwright Issues

```bash
# Install browsers
python -m playwright install

# Run with headed browser for debugging
pytest tests/e2e/ --headed
```

### Debug Failing Tests

```bash
# Run with pdb debugger
pytest tests/test_security.py --pdb

# Show print statements
pytest tests/test_security.py -s
```

## CI/CD Integration

Tests are automatically run in CI/CD pipeline on:

- Pull requests
- Push to develop/main branches

Configuration: `.github/workflows/test.yml` (if exists)

## Contributing

When adding new features, please:

1. Write tests first (TDD approach)
2. Ensure all tests pass
3. Maintain >80% code coverage
4. Update TEST_COVERAGE.txt
5. Add test documentation if needed
