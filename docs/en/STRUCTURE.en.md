[日本語](../STRUCTURE.md) | English

# MVC Directory Structure

This project follows the MVC (Model-View-Controller) pattern.

## Directory Structure

```
AccelMCP/
├── app/                          # Main application package
│   ├── __init__.py              # Application factory
│   ├── controllers/             # Controller layer
│   │   ├── __init__.py
│   │   ├── auth_controller.py   # Authentication (login/logout)
│   │   ├── admin_controller.py  # Admin interface routes
│   │   ├── api_controller.py    # RESTful API endpoints
│   │   └── mcp_controller.py    # MCP protocol endpoints
│   ├── models/                  # Model layer
│   │   ├── __init__.py
│   │   └── models.py            # DB models (McpService, Service, Capability, etc.)
│   ├── views/                   # View layer
│   │   ├── __init__.py
│   │   └── templates/           # HTML templates
│   ├── assets/                  # Static files (CSS, JS)
│   ├── services/                # Business logic layer
│   │   ├── __init__.py
│   │   ├── mcp_handler.py      # MCP request handling & relay
│   │   ├── mcp_logger.py       # Structured JSON connection logging
│   │   ├── mcp_discovery.py    # MCP service type detection
│   │   ├── audit_logger.py     # Admin audit & access logging
│   │   ├── template_sync.py    # Builtin template GitHub sync
│   │   └── variable_replacer.py # Variable expansion in URLs/headers
│   ├── config/                  # Configuration
│   │   ├── __init__.py
│   │   └── config.py            # Application configuration
│   └── utils/                   # Utilities
│       └── i18n.py              # Internationalization helper
├── db/                          # Database management
│   ├── migrate.py              # Migration management script
│   ├── migrations/             # Alembic migrations
│   └── seeds/                  # Initial data seeds
├── data/
│   └── builtin_templates/      # Builtin template definitions
├── tests/                       # Test suite
│   ├── unit/                   # Unit tests
│   └── e2e/                    # E2E tests (Playwright)
├── docs/                        # Documentation
├── run.py                       # Application startup script
├── run_check.sh                 # Code quality check script
├── run_format.sh               # Code format script
├── run_tests.sh                # Test runner script
├── setup_playwright.sh         # Playwright initial setup
├── requirements.txt            # Python dependencies
├── pyproject.toml              # Ruff/mypy configuration
├── Dockerfile                  # Docker image definition
└── compose.yaml                # Docker Compose configuration
```

## Role of Each Layer

### Controllers

Receive requests, call appropriate services or models, and return responses.

- **auth_controller.py**: Authentication processing (login/logout)
- **admin_controller.py**: Admin interface routing
- **api_controller.py**: RESTful API (CRUD operations)
- **mcp_controller.py**: MCP protocol endpoints

### Models

Handle database interactions. Define data structures.

- **models.py**:
  - `McpService` - MCP service definition
  - `Service` - Apps (mapped to apps table)
  - `Capability` - Tool definitions
  - `ConnectionAccount` - User accounts
  - `AccountPermission` - Account permissions
  - `McpConnectionLog` - MCP connection logs
  - `McpServiceTemplate` / `McpCapabilityTemplate` - Templates

### Views

Screens displayed to users. HTML templates and CSS.

- **templates/**: Jinja2 templates
- **assets/**: Static files (CSS, JavaScript, images)

### Services

Implement business logic. Processing between controllers and models.

- **mcp_handler.py**: MCP request processing, API/MCP relay, permission checking
- **mcp_logger.py**: Structured JSON output for MCP connection logs
- **mcp_discovery.py**: MCP service type auto-detection
- **audit_logger.py**: Admin operation audit log, login history
- **template_sync.py**: Builtin template sync from GitHub
- **variable_replacer.py**: Variable expansion in URLs and headers

### Config

Manage application configuration.

- **config.py**:
  - Database connection
  - Secret key
  - Debug mode, etc.

## Startup Method

### Local Development

```bash
python run.py
```

### Docker

```bash
docker compose up -d
```

## Import Paths

With the new structure, import as follows:

```python
# Models
from app.models.models import db, McpService, Service, Capability, ConnectionAccount, AccountPermission

# Services
from app.services.mcp_handler import MCPHandler

# Configuration
from app.config.config import Config
```

## Changes from Old Structure

- `app.py` → Split: `app/__init__.py` + `app/controllers/*`
- `models.py` → `app/models/models.py`
- `mcp_handler.py` → `app/services/mcp_handler.py`
- `templates/` → `app/views/templates/`
- `static/` → `app/assets/`
- DB management: SQL files → Flask-Migrate (Alembic) (`db/migrations/`)

## Advantages

1. **Separation of Concerns**: Each layer is clearly separated, improving maintainability
2. **Scalability**: Easy to place new features in appropriate locations
3. **Testability**: Each layer can be tested independently
4. **Readability**: File roles are clear
5. **Reusability**: Service layer logic can be used from multiple controllers

## Development Guidelines

### Adding New Features

1. **Adding New Endpoints**
   - Admin interface: `app/controllers/admin_controller.py`
   - API: `app/controllers/api_controller.py`
   - MCP: `app/controllers/mcp_controller.py`

2. **Adding New Models**
   - Add to `app/models/models.py`

3. **Adding New Business Logic**
   - Create a new service class in `app/services/`

4. **Adding New Configuration**
   - Add to `app/config/config.py`

### Coding Conventions

- **Controllers**: Use Blueprint
- **Models**: SQLAlchemy ORM
- **Services**: Class-based implementation
- **Naming Conventions**:
  - Files: snake_case (e.g., `auth_controller.py`)
  - Classes: PascalCase (e.g., `MCPHandler`)
  - Functions: snake_case (e.g., `get_capabilities`)

## Troubleshooting

### Import Errors

```python
# Correct
from app.models.models import User

# Incorrect
from models import User
```

### Template Not Found

- Check `template_folder='views/templates'` in `app/__init__.py`
- Paths are relative to `app/`

### Static Files Not Loading

- Check `static_folder='assets'` in `app/__init__.py`
- Reference as `/assets/style.css` in HTML
