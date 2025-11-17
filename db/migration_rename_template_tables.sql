-- Rename template tables to mcp_service_templates and mcp_capability_templates

-- Step 1: Rename service_templates to mcp_service_templates
RENAME TABLE service_templates TO mcp_service_templates;

-- Step 2: Rename capability_templates to mcp_capability_templates
RENAME TABLE capability_templates TO mcp_capability_templates;