# Octopus MCP Proxy Test Suite

English | [日本語](README.md)

## Overview

Comprehensive test suite for Octopus MCP Proxy covering unit tests, integration tests, and end-to-end tests.

## Test Structure

```
tests/
├── conftest.py                 # Pytest fixtures and configuration
├── conftest_playwright.py      # Playwright E2E test configuration
│
├── unit/                       # Unit tests (organized by category)
│   ├── admin/
│   │   └── test_admin_settings.py
│   ├── mcp/
│   │   ├── test_capability_integration.py
│   │   ├── test_capability_testing.py
│   │   ├── test_mcp_protocol.py
│   │   ├── test_mcp_services.py
│   │   ├── test_prompt_and_resource_capability.py
│   │   └── test_stdio_mcp.py
│   ├── security/
│   │   ├── test_permissions.py
│   │   └── test_security.py
│   ├── logging/
│   │   ├── test_connection_logs.py
│   │   └── test_log_search.py
│   ├── templates/
│   │   ├── test_prompt_templates.py
│   │   ├── test_template_import_export.py
│   │   └── test_variables.py
│   ├── ui/
│   │   ├── test_javascript_static.py
│   │   └── test_modal_and_sync.py
│   └── infrastructure/
│       ├── test_database_schema.py
│       ├── test_error_responses.py
│       ├── test_i18n.py
│       └── test_timeout_feature.py
│
├── e2e/                        # End-to-end tests
│   ├── test_login.py
│   ├── test_dashboard.py
│   ├── accounts/
│   ├── capabilities/
│   ├── mcp_templates/
│   └── services/
│
└── reports/                    # Test reports and documentation
    ├── TEST_COVERAGE.txt
    ├── TEST_SUMMARY.md
    ├── TEST_COMPLETION_REPORT.md
    ├── TEST_FINAL_REPORT.md
    ├── IMPORT_EXPORT_TESTS.md
    ├── PROMPT_RESOURCE_TESTS.md
    └── NEW_TESTS_SUMMARY.txt
```

## Running Tests

### All Tests

```bash
pytest tests/
```

### Unit Tests Only

```bash
pytest tests/unit/
```

### E2E Tests Only

```bash
pytest tests/e2e/
```

### Tests by Category

```bash
# Admin tests
pytest tests/unit/admin/

# MCP protocol and services tests
pytest tests/unit/mcp/

# Security and permissions tests
pytest tests/unit/security/

# Logging tests
pytest tests/unit/logging/

# Template and variables tests
pytest tests/unit/templates/

# UI tests
pytest tests/unit/ui/

# Infrastructure tests
pytest tests/unit/infrastructure/
```

### Specific Test File

```bash
pytest tests/unit/security/test_security.py
pytest tests/unit/templates/test_variables.py
pytest tests/unit/mcp/test_mcp_services.py
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
pytest tests/unit/security/test_security.py::TestBruteForceProtection::test_multiple_failed_logins_trigger_lock
```

## Test Categories

### Admin Tests (`unit/admin/`)

**test_admin_settings.py**

Tests for AdminSettings feature including:

- Settings CRUD operations
- Security settings (max_attempts, lock_duration, audit_retention)
- Language settings
- Settings integration with other features

### MCP Tests (`unit/mcp/`)

**test_mcp_protocol.py**

Tests for MCP protocol implementation including:

- MCP request/response handling
- Tool execution
- Protocol compliance

**test_mcp_services.py**

Tests for MCP Services feature including:

- MCP Service CRUD operations
- Subdomain vs path routing
- Access control (public/restricted)
- Apps association with MCP Services
- Toggle enabled/disabled state
- **YAML Export/Import**: Export MCP services with apps and capabilities, import with identifier collision handling

**test_capability_integration.py / test_capability_testing.py**

Tests for capability management and integration

**test_prompt_and_resource_capability.py**

Tests for prompt and resource capabilities

**test_stdio_mcp.py**

Tests for stdio transport protocol

### Security Tests (`unit/security/`)

**test_security.py**

Tests for security features including:

- Brute-force protection
- IP locking/unlocking
- Login failure tracking
- Lock expiration
- Admin login logs
- Admin action logs (audit trail)
- Security API endpoints

**test_permissions.py**

Tests for user permission management

### Logging Tests (`unit/logging/`)

**test_connection_logs.py**

Tests for MCP connection logging

**test_log_search.py**

Tests for log search and filtering functionality

### Template Tests (`unit/templates/`)

**test_prompt_templates.py**

Tests for prompt template management

**test_template_import_export.py**

Tests for Template Import/Export feature including:

- **YAML Export**: Export templates as YAML files with proper formatting
- **YAML Import**: Import templates from YAML with validation
- **Unicode Support**: Japanese and emoji characters in YAML
- **Roundtrip Testing**: Export and re-import produces equivalent data
- **Error Handling**: Invalid YAML format detection
- **Format Quality**: Human-readable YAML output

**test_variables.py**

Tests for Variables feature including:

- Variable CRUD operations
- Secret variables
- Environment variable references
- Variable replacement in URLs/headers
- Multiple variable replacement
- Missing variable handling

### UI Tests (`unit/ui/`)

**test_javascript_static.py**

Tests for JavaScript and static asset handling

**test_modal_and_sync.py**

Tests for modal dialogs and synchronization

### Infrastructure Tests (`unit/infrastructure/`)

**test_database_schema.py**

Tests for database schema and migrations

**test_error_responses.py**

Tests for error handling and response formatting

**test_i18n.py**

Tests for internationalization (i18n) support

**test_timeout_feature.py**

Tests for timeout configuration and handling

## Test Coverage

See `reports/TEST_COVERAGE.txt` for detailed coverage report.

### Current Coverage by Module

- **Models**: ~85% (includes new models: Variable, AdminSettings, LoginLockStatus, AdminLoginLog, AdminActionLog, McpService)
- **API Controllers**: ~80% (includes new endpoints for variables, mcp-services, security)
- **Views**: ~80%
- **MCP Protocol**: ~90%
- **E2E**: ~85%
- **Auth & Security**: ~90% (significantly improved)

## Test Reports

All test reports and documentation are located in the `reports/` directory:

- `TEST_COVERAGE.txt` - Detailed test coverage report
- `TEST_SUMMARY.md` - Summary of test implementation
- `TEST_COMPLETION_REPORT.md` - Test completion status
- `TEST_FINAL_REPORT.md` - Final test report
- `IMPORT_EXPORT_TESTS.md` - Import/Export feature test details
- `PROMPT_RESOURCE_TESTS.md` - Prompt and resource capability test details
- `NEW_TESTS_SUMMARY.txt` - Summary of newly added tests

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
