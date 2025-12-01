# MCP Server with Flask and FastMCP

HTTP/stdio compatible MCP server with API/MCP relay functionality and user-based permission management via a Web admin interface.

## Features

- **MCP Protocol Support**: Compatible with both HTTP and stdio
- **Relay Functionality**: Relay to API and MCP servers
- **Permission Management**: User-specific Tool usage permission control
- **Web Admin Interface**: Manage Services, Capabilities, and Accounts
- **Bearer Token Authentication**: Per-account token generation

## Starting the Server

```bash
# Start with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Access

- Web Admin Interface: http://admin.lvh.me:5000/ or http://localhost:5000/
- Default Administrator
  - ID: `accel`
  - Password: `universe`

**Note**: The `admin` subdomain is dedicated to the admin interface and is handled separately from service subdomains.

## Admin Interface Structure

### Login Screen

- Administrator authentication

### Service Management

- Service list display
- Create new service (subdomain, common headers)
- Service details/edit
- Capability management

### Capability Management

- Capability list
- Register capability (API/MCP selection, URL, headers, body configuration)
- Edit/delete capability

### Account Management

- Account list
- Register account (login ID, password)
- Account details (Bearer token display)
- Edit/delete account information

## MCP Client Connection

### Subdomain-Based Access (Recommended)

#### 1. Get Capabilities (GET Request)

```bash
# Using lvh.me domain (for local development)
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://myservice.lvh.me:5000/mcp

# Or using subdomain parameter
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:5000/mcp?subdomain=myservice
```

**Response Example:**

```json
{
  "capabilities": {
    "tools": [
      {
        "name": "get_weather",
        "description": "Get current weather information",
        "inputSchema": {
          "type": "object",
          "properties": {
            "city": {
              "type": "string",
              "description": "Parameter: city"
            }
          }
        }
      }
    ]
  },
  "serverInfo": {
    "name": "Weather Service",
    "version": "1.0.0"
  }
}
```

#### 2. Execute Tool (POST Request)

```bash
# Execute tool directly
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"arguments": {"city": "Tokyo"}}' \
  http://myservice.lvh.me:5000/tools/get_weather

# Or execute via MCP protocol
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "get_weather",
      "arguments": {"city": "Tokyo"}
    }
  }' \
  http://myservice.lvh.me:5000/mcp
```

### MCP Client Configuration

#### HTTP Connection (Dify, Claude Desktop, etc.)

```json
{
  "mcpServers": {
    "my-service": {
      "url": "http://myservice.lvh.me:5000/mcp",
      "transport": {
        "type": "http"
      },
      "headers": {
        "Authorization": "Bearer YOUR_TOKEN"
      }
    }
  }
}
```

#### Legacy Endpoint (Backward Compatibility)

```json
{
  "mcpServers": {
    "my-service": {
      "url": "http://localhost:5000/mcp/myservice",
      "headers": {
        "Authorization": "Bearer YOUR_TOKEN"
      }
    }
  }
}
```

### stdio Connection

```json
{
  "mcpServers": {
    "my-service": {
      "command": "docker",
      "args": [
        "exec",
        "-i",
        "mcp_server",
        "python",
        "stdio_server.py",
        "myservice",
        "YOUR_TOKEN"
      ]
    }
  }
}
```

## Endpoint List

### MCP Endpoints

| Endpoint                                  | Method | Description                                   |
| ----------------------------------------- | ------ | --------------------------------------------- |
| `<subdomain>.lvh.me:5000/mcp`             | GET    | Get Capabilities available to the account     |
| `<subdomain>.lvh.me:5000/mcp`             | POST   | Process MCP requests (tools/list, tools/call) |
| `<subdomain>.lvh.me:5000/tools/<tool_id>` | POST   | Execute a specific Tool directly              |
| `/mcp/<subdomain>`                        | POST   | Legacy endpoint (backward compatibility)      |

**Note:** `lvh.me` is a domain for local development that always resolves to 127.0.0.1. Use your own domain in production.

## Database Structure

- **users**: User information, authentication data
- **services**: Registered services (subdomain, common headers)
- **capabilities**: Tool definitions (API/MCP, URL, headers, body)
- **user_permissions**: User × Capability permission mapping

## Development

```bash
# Develop locally
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
