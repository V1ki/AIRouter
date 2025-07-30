import asyncio
import logging
from typing import Dict, Optional, Tuple, List
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.provider import ApiKey, ModelImplementation

logger = logging.getLogger(__name__)


class ConcurrencyTracker:
    """Track concurrent requests per API key with thread-safe operations."""
    
    def __init__(self):
        self._concurrent_requests: Dict[UUID, int] = {}
        self._lock = asyncio.Lock()
        self._key_locks: Dict[UUID, asyncio.Lock] = {}
        
    async def get_concurrent_count(self, api_key_id: UUID) -> int:
        """Get current concurrent request count for an API key."""
        async with self._lock:
            return self._concurrent_requests.get(api_key_id, 0)
    
    async def increment(self, api_key_id: UUID) -> int:
        """Increment concurrent request count for an API key."""
        async with self._lock:
            count = self._concurrent_requests.get(api_key_id, 0) + 1
            self._concurrent_requests[api_key_id] = count
            
            # Create a lock for this key if it doesn't exist
            if api_key_id not in self._key_locks:
                self._key_locks[api_key_id] = asyncio.Lock()
                
            logger.debug(f"API key {api_key_id} concurrent requests: {count}")
            return count
    
    async def decrement(self, api_key_id: UUID) -> int:
        """Decrement concurrent request count for an API key."""
        async with self._lock:
            count = max(0, self._concurrent_requests.get(api_key_id, 1) - 1)
            self._concurrent_requests[api_key_id] = count
            
            # Clean up if no active requests
            if count == 0 and api_key_id in self._concurrent_requests:
                del self._concurrent_requests[api_key_id]
                
            logger.debug(f"API key {api_key_id} concurrent requests: {count}")
            return count
    
    async def get_all_counts(self) -> Dict[UUID, int]:
        """Get all current concurrent request counts."""
        async with self._lock:
            return self._concurrent_requests.copy()


class ApiKeyConcurrencyConfig:
    """Configuration for API key concurrency limits."""
    
    def __init__(self, default_limit: int = 10):
        self.default_limit = default_limit
        self._custom_limits: Dict[UUID, int] = {}
        self._lock = asyncio.Lock()
        
    async def set_limit(self, api_key_id: UUID, limit: int):
        """Set a custom concurrency limit for an API key."""
        async with self._lock:
            self._custom_limits[api_key_id] = limit
            
    async def get_limit(self, api_key_id: UUID, db_limit: Optional[int] = None) -> int:
        """
        Get the concurrency limit for an API key.
        
        Priority:
        1. Runtime custom limit (if set via API)
        2. Database stored limit (if exists)
        3. Default limit
        """
        async with self._lock:
            # Check runtime custom limit first
            if api_key_id in self._custom_limits:
                return self._custom_limits[api_key_id]
            # Then check database limit
            if db_limit is not None:
                return db_limit
            # Finally use default
            return self.default_limit
    
    async def remove_limit(self, api_key_id: UUID):
        """Remove custom limit for an API key (revert to default)."""
        async with self._lock:
            if api_key_id in self._custom_limits:
                del self._custom_limits[api_key_id]


class ConcurrencyManager:
    """Manage API key selection based on concurrent request limits."""
    
    def __init__(self, config: Optional[ApiKeyConcurrencyConfig] = None):
        self.tracker = ConcurrencyTracker()
        self.config = config or ApiKeyConcurrencyConfig()
        
    async def select_api_key_with_capacity(
        self, 
        api_keys: List[ApiKey],
        max_retries: int = 3
    ) -> Optional[ApiKey]:
        """
        Select an API key that has available capacity.
        
        Args:
            api_keys: List of API keys to choose from (already sorted by preference)
            max_retries: Maximum number of times to check all keys
            
        Returns:
            ApiKey if one with capacity is found, None otherwise
        """
        for retry in range(max_retries):
            for api_key in api_keys:
                current_count = await self.tracker.get_concurrent_count(api_key.id)
                # Pass the database limit if available
                limit = await self.config.get_limit(api_key.id, api_key.concurrency_limit)
                
                if current_count < limit:
                    logger.info(
                        f"Selected API key {api_key.alias} ({api_key.id}) "
                        f"with {current_count}/{limit} concurrent requests"
                    )
                    return api_key
                    
            # If no key has capacity, wait a bit before retrying
            if retry < max_retries - 1:
                await asyncio.sleep(0.1 * (retry + 1))  # Exponential backoff
                
        logger.warning("All API keys are at capacity")
        return None
    
    @asynccontextmanager
    async def track_request(self, api_key_id: UUID):
        """
        Context manager to track a request's lifecycle.
        
        Usage:
            async with manager.track_request(api_key_id):
                # Make API call
                pass
        """
        try:
            await self.tracker.increment(api_key_id)
            yield
        finally:
            await self.tracker.decrement(api_key_id)
    
    async def get_usage_stats(self, db: Optional[Session] = None) -> Dict[UUID, Dict[str, int]]:
        """Get current usage statistics for all API keys."""
        current_counts = await self.tracker.get_all_counts()
        stats = {}
        
        for api_key_id, current_count in current_counts.items():
            # Get database limit if db session provided
            db_limit = None
            if db:
                api_key = db.query(ApiKey).filter(ApiKey.id == api_key_id).first()
                if api_key:
                    db_limit = api_key.concurrency_limit
            
            limit = await self.config.get_limit(api_key_id, db_limit)
            stats[api_key_id] = {
                "current": current_count,
                "limit": limit,
                "available": limit - current_count
            }
            
        return stats


# Global instance
_concurrency_manager: Optional[ConcurrencyManager] = None


def get_concurrency_manager() -> ConcurrencyManager:
    """Get the global concurrency manager instance."""
    global _concurrency_manager
    if _concurrency_manager is None:
        _concurrency_manager = ConcurrencyManager()
    return _concurrency_manager


async def select_implementation_with_concurrency(
    db: Session,
    implementations: List[ModelImplementation],
    original_selector_func
) -> Tuple[Optional[ModelImplementation], Optional[ApiKey]]:
    """
    Enhanced implementation selector that considers concurrency limits.
    
    This wraps the original get_best_implementation logic to add concurrency checking.
    """
    manager = get_concurrency_manager()
    
    # Get the original selection (without concurrency consideration)
    best_impl, best_key = original_selector_func(db, implementations)
    
    if not best_impl or not best_key:
        return None, None
    
    # Check if the selected key has capacity
    current_count = await manager.tracker.get_concurrent_count(best_key.id)
    limit = await manager.config.get_limit(best_key.id, best_key.concurrency_limit)
    
    if current_count < limit:
        return best_impl, best_key
    
    # If not, try to find another implementation/key combination with capacity
    from app.models.provider import ApiKey as DBApiKey
    
    for implementation in implementations:
        provider = implementation.provider
        
        # Get all API keys for this provider, sorted by preference
        api_keys = db.query(DBApiKey).filter(
            DBApiKey.provider_id == provider.id
        ).order_by(DBApiKey.sort_order).all()
        
        # Find a key with available capacity
        selected_key = await manager.select_api_key_with_capacity(api_keys)
        if selected_key:
            return implementation, selected_key
    
    # If all keys are at capacity, return None
    logger.warning("All API keys across all implementations are at capacity")
    return None, None