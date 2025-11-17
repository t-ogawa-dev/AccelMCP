-- Migration: Remove login_id and password_hash, add notes field
-- Date: 2025-11-13

USE mcp_server;

-- Add notes column
ALTER TABLE users ADD COLUMN notes TEXT AFTER bearer_token;

-- Remove login_id and password_hash columns
ALTER TABLE users DROP COLUMN login_id;

ALTER TABLE users DROP COLUMN password_hash;