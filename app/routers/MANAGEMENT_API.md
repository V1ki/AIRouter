# Management API Documentation

This document describes the management API endpoints for the AI Router frontend interface.

## Base URL
All management endpoints are prefixed with `/api`.

## Authentication
Currently, these endpoints do not require authentication. In production, you should add appropriate authentication middleware.

## Endpoints

### Provider Management

#### GET /api/providers
Get all providers with pagination.

Query Parameters:
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum number of records to return (default: 100)

#### POST /api/providers
Create a new provider.

Request Body:
```json
{
  "name": "Provider Name",
  "base_url": "https://api.provider.com",
  "description": "Optional description",
  "free_quota_type": "CREDIT" // Optional: CREDIT, SHARED_TOKENS, PER_MODEL_TOKENS
}
```

#### PUT /api/providers/{provider_id}
Update an existing provider.

#### DELETE /api/providers/{provider_id}
Delete a provider.

### API Key Management

#### GET /api/api-keys
Get all API keys with optional filtering.

Query Parameters:
- `provider_id` (optional): Filter by provider UUID
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum number of records to return (default: 100)

#### POST /api/api-keys
Create a new API key.

Request Body:
```json
{
  "provider_id": "uuid",
  "alias": "My API Key",
  "key": "sk-...",
  "sort_order": 0
}
```

#### PUT /api/api-keys/{api_key_id}
Update an existing API key.

#### DELETE /api/api-keys/{api_key_id}
Delete an API key.

### Model Management

#### GET /api/models
Get all models with pagination.

Query Parameters:
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum number of records to return (default: 100)

#### POST /api/models
Create a new model.

Request Body:
```json
{
  "name": "gpt-4",
  "description": "GPT-4 model",
  "capabilities": ["text-generation", "chat"],
  "family": "openai"
}
```

#### PUT /api/models/{model_id}
Update an existing model.

#### DELETE /api/models/{model_id}
Delete a model.

### Model Implementation Management

#### GET /api/model-implementations
Get all model implementations with optional filtering.

Query Parameters:
- `provider_id` (optional): Filter by provider UUID
- `model_id` (optional): Filter by model UUID
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum number of records to return (default: 100)

#### POST /api/model-implementations
Create a new model implementation.

Request Body:
```json
{
  "provider_id": "uuid",
  "model_id": "uuid",
  "provider_model_id": "gpt-4-turbo",
  "version": "2024-01-01",
  "context_window": 128000,
  "pricing_info": {
    "input_price": 0.01,
    "output_price": 0.03
  },
  "is_available": true,
  "custom_parameters": {},
  "sort_order": 0
}
```

#### PUT /api/model-implementations/{implementation_id}
Update an existing model implementation.

#### DELETE /api/model-implementations/{implementation_id}
Delete a model implementation.

### Usage Statistics

#### GET /api/usage/stats
Get aggregated usage statistics.

Query Parameters:
- `start_date` (optional): Start date for filtering (YYYY-MM-DD)
- `end_date` (optional): End date for filtering (YYYY-MM-DD)
- `group_by` (optional): Group by "day", "week", "month", "provider", or "model" (default: "day")

Response format varies by group_by:
- Time-based grouping returns: `period`, `total_prompt_tokens`, `total_completion_tokens`, `total_tokens`, `request_count`
- Provider/Model grouping returns: `group_name`, `total_prompt_tokens`, `total_completion_tokens`, `total_tokens`, `request_count`

#### GET /api/usage
Get detailed usage records.

Query Parameters:
- `start_date` (optional): Start date for filtering (ISO 8601 datetime)
- `end_date` (optional): End date for filtering (ISO 8601 datetime)
- `api_key_id` (optional): Filter by API key UUID
- `model_implementation_id` (optional): Filter by model implementation UUID
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum number of records to return (default: 100)

## Error Handling

All endpoints return appropriate HTTP status codes:
- `200 OK`: Successful operation
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

Error responses include a detail message:
```json
{
  "detail": "Error description"
}
```

## Example Usage

```bash
# Get all providers
curl http://localhost:8000/api/providers

# Create a new provider
curl -X POST http://localhost:8000/api/providers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "OpenAI",
    "base_url": "https://api.openai.com/v1",
    "description": "OpenAI API"
  }'

# Get usage statistics grouped by provider
curl "http://localhost:8000/api/usage/stats?group_by=provider&start_date=2024-01-01"
```