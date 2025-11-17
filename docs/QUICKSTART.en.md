# Quick Start - Try the MCP Server in 5 Minutes

This guide explains the quickest way to start and test the MCP server.

## 1. Start Server (1 minute)

```bash
cd /Users/takahisaogawa/test/test2
docker-compose up -d
```

Wait for startup:

```bash
docker-compose logs -f web
```

Once you see `Default admin user created`, the server is ready.

## 2. Login to Admin Interface (1 minute)

1. Open http://localhost:5001 in your browser
2. Login:
   - ID: `accel`
   - Password: `universe`

## 3. Create Test Service (2 minutes)

### 3.1 Register Service

1. Dashboard → "Service Management"
2. Click "New Service Registration"
3. Enter:
   - **Service Name**: Weather Service
   - **Subdomain**: weather
   - **Description**: Test weather service
4. Click "Register"

### 3.2 Register Capability

1. Click the created service
2. Click "Capabilities Management"
3. Click "New Capability Registration"
4. Enter:
   - **Capability Name**: echo_test
   - **Connection Type**: API
   - **Connection URL**: https://httpbin.org/post
   - **Description**: Simple echo test
   - **Body Parameters**:
     ```
     message: Hello
     ```
5. Click "Register"

### 3.3 Grant Permission to Administrator

1. Dashboard → "Account Management"
2. Click "Administrator"
3. The capability permissions are automatically assigned to accounts
4. Verify the capability appears in the account's capability list

### 3.4 Get Bearer Token

On the same account details screen, **copy the Bearer Token**.

## 4. Test MCP Endpoint (1 minute)

### 4.1 Get Capabilities

```bash
# Replace TOKEN with your actual token
TOKEN="YOUR_BEARER_TOKEN_HERE"

curl -H "Authorization: Bearer $TOKEN" \
  http://weather.lvh.me:5001/mcp
```

**Expected Output:**

```json
{
  "capabilities": {
    "tools": [
      {
        "name": "echo_test",
        "description": "Simple echo test",
        "inputSchema": {
          "type": "object",
          "properties": {
            "message": {
              "type": "string",
              "description": "Parameter: message",
              "default": "Hello"
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

### 4.2 Execute Tool

```bash
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"arguments": {"message": "Test from MCP"}}' \
  http://weather.lvh.me:5001/tools/echo_test
```

**Expected Output:**

```json
{
  "content": [
    {
      "type": "text",
      "text": "{\"success\": true, \"status_code\": 200, \"data\": {...}}"
    }
  ],
  "isError": false
}
```

## 5. Run Test Script

If you have a test script available:

```bash
# Edit and set your token
# Change BEARER_TOKEN = "YOUR_BEARER_TOKEN_HERE"
# Set SUBDOMAIN = "weather"

python3 test_mcp.py
```

## Done! 🎉

You can now:

✅ Start the MCP server  
✅ Manage services, capabilities, and permissions via Web admin  
✅ Access subdomain-based MCP endpoints  
✅ Execute tools and verify responses

## Next Steps

### Integrate Real APIs

1. Create new Capabilities in the Web admin
2. Set real API URLs (OpenWeather, GitHub, etc.)
3. Configure API Keys in header parameters
4. Grant permissions to accounts
5. Use from MCP clients (Dify, Claude Desktop)

### Manage Multiple Services

1. Create services for each API
2. Separate by subdomain (weather, github, database, etc.)
3. Set different permissions per account

### Relay MCP Servers

1. Register other MCP servers as Capabilities
2. Set type to "MCP"
3. Consolidate multiple MCP servers into one

## Troubleshooting

### lvh.me not working

Use this instead:

```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5001/mcp?subdomain=weather
```

### Permission Errors

1. Check permissions are correctly set in account details
2. Verify capability name is correct
3. Confirm subdomain is correct

### Database Errors

```bash
# Restart containers
docker-compose restart

# Or fully rebuild
docker-compose down
docker-compose up -d --build
```

## Additional Documentation

- **Detailed Setup**: `SETUP.en.md`
- **MCP Endpoint Details**: `MCP_ENDPOINTS.en.md`
- **Project Overview**: `README.en.md`
