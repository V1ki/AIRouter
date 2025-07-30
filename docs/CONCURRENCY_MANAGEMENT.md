# API Key Concurrency Management

This feature provides automatic API key switching based on concurrent request limits, ensuring optimal resource utilization and preventing API rate limit issues.

## Overview

The concurrency management system tracks active requests per API key and automatically switches to the next available key when a key reaches its concurrent request limit. This provides:

- **Automatic load balancing** across multiple API keys
- **Prevention of rate limit errors** by respecting concurrency limits
- **Real-time monitoring** of API key usage
- **Configurable limits** per API key

## Architecture

### Components

1. **ConcurrencyTracker**: Tracks active requests per API key with thread-safe operations
2. **ApiKeyConcurrencyConfig**: Manages concurrency limits with database persistence
3. **ConcurrencyManager**: Orchestrates key selection and request lifecycle tracking
4. **Concurrency API**: REST endpoints for configuration and monitoring

### How It Works

1. When a request arrives, the system checks all available API keys
2. It selects the first key that has available capacity (current < limit)
3. The request is tracked throughout its lifecycle
4. When the request completes, the concurrent count is decremented
5. If all keys are at capacity, the system retries with exponential backoff

## Configuration

### Setting Concurrency Limits

Limits can be set in three ways (in order of priority):

1. **Runtime API** - Immediate effect, not persisted across restarts
2. **Database** - Persisted configuration
3. **Default** - System default (10 concurrent requests)

### API Endpoints

#### Get Concurrency Statistics
```bash
GET /api/concurrency/stats
```

Response:
```json
[
  {
    "api_key_id": "uuid",
    "api_key_alias": "production-key-1",
    "current": 3,
    "limit": 5,
    "available": 2,
    "provider_name": "OpenAI"
  }
]
```

#### Set Concurrency Limit
```bash
PUT /api/concurrency/limits/{api_key_id}
Content-Type: application/json

{
  "limit": 5
}
```

#### Reset to Default Limit
```bash
DELETE /api/concurrency/limits/{api_key_id}
```

#### Get Configuration
```bash
GET /api/concurrency/config
```

## Database Schema

The `api_keys` table includes:
```sql
concurrency_limit INTEGER DEFAULT NULL
```

- `NULL` means use the system default limit
- Positive integers set a custom limit for that key

## Usage Example

### Python Client
```python
import asyncio
import aiohttp

async def test_concurrency():
    async with aiohttp.ClientSession() as session:
        # Set a low limit for testing
        await session.put(
            "http://localhost:8000/api/concurrency/limits/your-key-id",
            json={"limit": 2}
        )
        
        # Make multiple concurrent requests
        tasks = []
        for i in range(5):
            task = session.post(
                "http://localhost:8000/v1/chat/completions",
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": "Hello"}]
                }
            )
            tasks.append(task)
        
        # The system will automatically use different API keys
        responses = await asyncio.gather(*tasks)
```

### Testing Script

A comprehensive test script is provided:
```bash
# Run the test
python test_concurrency.py

# Reset all limits to default
python test_concurrency.py --reset
```

## Implementation Details

### Thread Safety

- All concurrent request counting uses asyncio locks
- Database operations are atomic
- No race conditions in key selection

### Request Lifecycle

1. **Selection Phase**: Choose API key with available capacity
2. **Tracking Phase**: Increment concurrent count
3. **Execution Phase**: Make the actual API call
4. **Cleanup Phase**: Decrement count (even on errors)

### Edge Cases Handled

1. **All keys at capacity**: Retry with exponential backoff
2. **Key removed during request**: Graceful degradation
3. **Database unavailable**: Falls back to runtime config
4. **Streaming requests**: Proper lifecycle tracking

## Migration

Run the following SQL to add the concurrency limit column:
```sql
ALTER TABLE api_keys 
ADD COLUMN concurrency_limit INTEGER DEFAULT NULL;
```

## Monitoring

Monitor the system health by checking:

1. **Current usage** via `/api/concurrency/stats`
2. **Capacity issues** in application logs
3. **Response times** to detect queueing

## Best Practices

1. **Set realistic limits** based on your provider's rate limits
2. **Monitor usage patterns** to optimize limits
3. **Use multiple keys** for better distribution
4. **Set higher limits** for production keys
5. **Lower limits** for development/test keys

## Troubleshooting

### All requests failing with "No suitable API key"
- Check if all keys are at their concurrency limits
- Increase limits or add more API keys

### Uneven distribution across keys
- Check the `sort_order` field in API keys
- Ensure keys have appropriate limits

### High latency
- Monitor if requests are queueing
- Increase concurrency limits or add more keys