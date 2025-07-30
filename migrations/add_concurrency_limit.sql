-- Migration: Add concurrency_limit column to api_keys table
-- Date: 2025-01-29

-- Add concurrency_limit column to api_keys table
ALTER TABLE api_keys 
ADD COLUMN concurrency_limit INTEGER DEFAULT NULL;

-- Add comment to explain the column
COMMENT ON COLUMN api_keys.concurrency_limit IS 'Custom concurrency limit for this API key. NULL means use default limit.';

-- Example: Set a custom limit for specific API keys
-- UPDATE api_keys SET concurrency_limit = 5 WHERE alias = 'production-key-1';
-- UPDATE api_keys SET concurrency_limit = 20 WHERE alias = 'high-traffic-key';