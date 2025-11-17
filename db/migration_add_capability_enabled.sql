-- Migration: Add is_enabled column to capability_templates table

ALTER TABLE capability_templates
ADD COLUMN is_enabled BOOLEAN DEFAULT TRUE NOT NULL COMMENT 'Capability有効/無効フラグ';