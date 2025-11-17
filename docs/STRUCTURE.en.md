# MVC Directory Structure

This project follows the MVC (Model-View-Controller) pattern.

## Directory Structure

```
test2/
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
│   │   └── models.py            # Database models (User, Service, Capability, etc.)
│   ├── views/                   # View layer
│   │   ├── __init__.py
│   │   └── templates/           # HTML templates
│   │       ├── login.html
│   │       ├── dashboard.html
│   │       ├── services/        # Service management screens
│   │       ├── capabilities/    # Capability management screens
│   │       └── users/          # Account management screens
│   ├── assets/                  # Static files (formerly static)
│   │   └── style.css           # CSS styles
│   ├── services/                # Business logic layer
│   │   ├── __init__.py
│   │   └── mcp_handler.py      # MCP processing logic
│   └── config/                  # Configuration files
│       ├── __init__.py
│       └── config.py            # Application configuration
├── run.py                       # Application startup script
├── stdio_server.py             # stdio MCP server
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker image definition
├── compose.yaml                # Docker Compose configuration
├── init.sql                    # DB initialization script
└── docs/                       # Documentation
    ├── README.md
    ├── SETUP.md
    ├── QUICKSTART.md
    └── MCP_ENDPOINTS.md
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
  - User - User information
  - Service - Service definitions
  - Capability - Tool definitions
  - UserPermission - User permissions

### Views

Screens displayed to users. HTML templates and CSS.

- **templates/**: Jinja2 templates
- **assets/**: Static files (CSS, JavaScript, images)

### Services

Implement business logic. Processing between controllers and models.

- **mcp_handler.py**:
  - MCP request processing
  - API/MCP relay
  - Permission checking

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
docker-compose up -d
```

## Import Paths

With the new structure, import as follows:

```python
# Models
from app.models.models import db, User, Service, Capability, UserPermission

# Services
from app.services.mcp_handler import MCPHandler

# Configuration
from app.config.config import Config
```

## Changes from Old Structure

### Before

```
test2/
├── app.py              # All route definitions
├── models.py           # Model definitions
├── mcp_handler.py      # MCP processing
├── templates/          # Templates
└── static/             # Static files
```

### After (MVC Structure)

- `app.py` → Split: `app/__init__.py` + `app/controllers/*`
- `models.py` → `app/models/models.py`
- `mcp_handler.py` → `app/services/mcp_handler.py`
- `templates/` → `app/views/templates/`
- `static/` → `app/assets/`

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
