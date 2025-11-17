# MCP Endpoint Detailed Guide

This document explains the detailed usage of each MCP server endpoint.

## Overview

This MCP server provides 3 main endpoints:

1. **GET /mcp** - Get Capabilities list
2. **POST /mcp** - Process MCP protocol requests
3. **POST /tools/<tool_id>** - Direct Tool execution

All endpoints support subdomain-based routing.
The admin interface is accessible at `http://admin.lvh.me:5001/`.

## Subdomain Specification Methods

### Method 1: lvh.me Domain (Recommended)

`lvh.me` always points to 127.0.0.1, making it convenient for local development.

```
http://<subdomain>.lvh.me:5001/mcp
```

**Examples:**

- `http://weather.lvh.me:5001/mcp` - weather service MCP endpoint
- `http://myapi.lvh.me:5001/mcp` - myapi service MCP endpoint
- `http://admin.lvh.me:5001/` - Admin interface (subdomain admin is dedicated to admin interface)

### Method 2: Query Parameters

```
http://localhost:5001/mcp?subdomain=<subdomain>
```

### Method 3: Custom Header

```bash
curl -H "X-Subdomain: myservice" http://localhost:5001/mcp
```

## Authentication

All requests require an `Authorization` header:

```
Authorization: Bearer <USER_BEARER_TOKEN>
```

The account's Bearer token can be found on the account details page in the web admin interface.

---

## 1. GET /mcp - Get Capabilities

Retrieve the list of Tools available to the account.

### Request

```bash
curl -H "Authorization: Bearer abc123..." \
  http://myservice.lvh.me:5001/mcp
```

### Response

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
              "description": "Parameter: city",
              "default": "Tokyo"
            },
            "units": {
              "type": "string",
              "description": "Parameter: units",
              "default": "metric"
            }
          },
          "required": []
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

### Behavior

1. Identify service from subdomain
2. Identify account from Bearer token
3. Return only Capabilities the account has permission for
4. Each Capability's InputSchema is auto-generated from registered Body parameters

---

## 2. POST /mcp - MCP Protocol Requests

Process requests according to the standard MCP protocol.

### Supported Methods

- `tools/list` - Get Tool list (equivalent to GET /mcp)
- `tools/call` - Execute Tool

### 2.1 tools/list

#### Request

```bash
curl -X POST \
  -H "Authorization: Bearer abc123..." \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
  }' \
  http://myservice.lvh.me:5001/mcp
```

#### Response

```json
{
  "jsonrpc": "2.0",
  "result": {
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
  }
}
```

### 2.2 tools/call

#### Request

```bash
curl -X POST \
  -H "Authorization: Bearer abc123..." \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "get_weather",
      "arguments": {
        "city": "Tokyo"
      }
    }
  }' \
  http://myservice.lvh.me:5001/mcp
```

#### Response (Success)

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"success\": true, \"data\": {\"temperature\": 25, \"condition\": \"sunny\"}}"
      }
    ]
  }
}
```

#### Response (Permission Error)

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "error": {
    "code": -32603,
    "message": "Permission denied for tool: get_weather"
  }
}
```

---

## 3. POST /tools/<tool_id> - Direct Tool Execution

Simple endpoint to execute a Tool by directly specifying its ID.

### Request

```bash
curl -X POST \
  -H "Authorization: Bearer abc123..." \
  -H "Content-Type: application/json" \
  -d '{
    "arguments": {
      "city": "Tokyo"
    }
  }' \
  http://myservice.lvh.me:5001/tools/get_weather
```

### Tool ID Specification Methods

- **Capability Name** (recommended): `get_weather`
- **Capability ID**: `1`, `2`, `3`, etc.

### Response (Success)

```json
{
  "content": [
    {
      "type": "text",
      "text": "{\"success\": true, \"data\": {\"temperature\": 25}}"
    }
  ],
  "isError": false
}
```

### Response (Permission Error)

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32000,
    "message": "Permission denied for tool: get_weather"
  }
}
```

### Response (Tool Not Found)

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32602,
    "message": "Tool not found: invalid_tool"
  }
}
```

---

## Error Code List

| Code   | Description                                    |
| ------ | ---------------------------------------------- |
| -32700 | Parse error - Invalid JSON                     |
| -32600 | Invalid Request - Subdomain not specified      |
| -32601 | Method not found - Unsupported method          |
| -32602 | Invalid params - Tool not found                |
| -32603 | Internal error - Execution error               |
| -32000 | Server error - Authentication/Permission error |
| -32001 | Server error - Service not found               |

---

## Usage Examples

### Example 1: Dify Configuration

```json
{
  "mcp_servers": {
    "weather_service": {
      "url": "http://weather.lvh.me:5001/mcp",
      "auth": {
        "type": "bearer",
        "token": "YOUR_BEARER_TOKEN"
      }
    }
  }
}
```

### Example 2: Claude Desktop Configuration

```json
{
  "mcpServers": {
    "weather": {
      "url": "http://weather.lvh.me:5001/mcp",
      "transport": {
        "type": "http"
      },
      "headers": {
        "Authorization": "Bearer YOUR_BEARER_TOKEN"
      }
    }
  }
}
```

### Example 3: Python Script Usage

```python
import requests

headers = {
    'Authorization': 'Bearer YOUR_BEARER_TOKEN',
    'Content-Type': 'application/json'
}

# Get Capabilities
response = requests.get(
    'http://myservice.lvh.me:5001/mcp',
    headers=headers
)
capabilities = response.json()
print(capabilities)

# Execute Tool
response = requests.post(
    'http://myservice.lvh.me:5001/tools/get_weather',
    headers=headers,
    json={'arguments': {'city': 'Tokyo'}}
)
result = response.json()
print(result)
```

### Example 4: Complete Workflow with cURL

```bash
# 1. Get Capabilities
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://myservice.lvh.me:5001/mcp

# 2. Execute specific Tool
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"arguments": {"city": "Tokyo"}}' \
  http://myservice.lvh.me:5001/tools/get_weather

# 3. Execute Tool via MCP protocol
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
  http://myservice.lvh.me:5001/mcp
```

---

## Implementation Flow

### GET /mcp or POST /mcp (tools/list)

```
1. Receive request
   ↓
2. Extract subdomain (lvh.me, query parameter, header)
   ↓
3. Verify Bearer token
   ↓
4. Search for Service by subdomain
   ↓
5. Get Capabilities with permissions by account ID and Service ID
   ↓
6. Format and return Capability list
```

### POST /tools/<tool_id>

```
1. Receive request
   ↓
2. Extract subdomain
   ↓
3. Verify Bearer token
   ↓
4. Search for Service by subdomain
   ↓
5. Search for Capability by tool_id (name or ID)
   ↓
6. Check account permissions
   ↓
7. With permission → Execute Capability (API/MCP relay)
   Without permission → Error response
   ↓
8. Return result
```

### POST /mcp (tools/call)

```
1. Receive request
   ↓
2. Extract subdomain
   ↓
3. Verify Bearer token
   ↓
4. Search for Service by subdomain
   ↓
5. Search for Capability by params.name
   ↓
6. Check account permissions
   ↓
7. With permission → Execute Capability
   Without permission → JSON-RPC error response
   ↓
8. Return result in JSON-RPC format
```

---

## Troubleshooting

### Subdomain Not Recognized

**Problem:** Subdomain is not recognized when accessing via lvh.me

**Solution:**

1. Check DNS settings (`ping myservice.lvh.me` should return 127.0.0.1)
2. Use query parameter instead: `?subdomain=myservice`
3. Include port number: `http://myservice.lvh.me:5001/mcp`

### Authentication Error

**Problem:** `Invalid bearer token` error

**Solution:**

1. Verify Bearer token (Web admin interface > Account details)
2. Check `Authorization: Bearer ` format (includes space)
3. Regenerate token

### Permission Error

**Problem:** `Permission denied for tool: xxx`

**Solution:**

1. Check account permissions in web admin interface
2. Add the relevant Capability in Account details > Permission management

### Tool Not Found Error

**Problem:** `Tool not found: xxx`

**Solution:**

1. Confirm Capability is properly registered
2. Check for spelling errors in Tool name
3. Verify accessing the correct service (subdomain)
