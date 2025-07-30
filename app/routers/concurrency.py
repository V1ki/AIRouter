from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Optional
from uuid import UUID
from pydantic import BaseModel

from app.db.database import get_db
from app.services.concurrency_manager import get_concurrency_manager
from app.models.provider import ApiKey

router = APIRouter(prefix="/concurrency", tags=["Concurrency Management"])


class ConcurrencyLimitUpdate(BaseModel):
    """Model for updating concurrency limit."""
    limit: int


class ConcurrencyStats(BaseModel):
    """Model for concurrency statistics."""
    api_key_id: UUID
    api_key_alias: str
    current: int
    limit: int
    available: int
    provider_name: str


@router.get("/stats", response_model=list[ConcurrencyStats])
async def get_concurrency_stats(
    db: Session = Depends(get_db)
) -> list[ConcurrencyStats]:
    """Get current concurrency statistics for all API keys."""
    manager = get_concurrency_manager()
    stats = await manager.get_usage_stats(db)  # Pass db to get database limits
    
    result = []
    for api_key_id, stat in stats.items():
        # Get API key details from database
        api_key = db.query(ApiKey).filter(ApiKey.id == api_key_id).first()
        if api_key:
            result.append(ConcurrencyStats(
                api_key_id=api_key_id,
                api_key_alias=api_key.alias,
                current=stat["current"],
                limit=stat["limit"],
                available=stat["available"],
                provider_name=api_key.provider.name
            ))
    
    return result


@router.get("/stats/{api_key_id}", response_model=ConcurrencyStats)
async def get_api_key_concurrency_stats(
    api_key_id: UUID,
    db: Session = Depends(get_db)
) -> ConcurrencyStats:
    """Get concurrency statistics for a specific API key."""
    # Verify API key exists
    api_key = db.query(ApiKey).filter(ApiKey.id == api_key_id).first()
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")
    
    manager = get_concurrency_manager()
    current = await manager.tracker.get_concurrent_count(api_key_id)
    limit = await manager.config.get_limit(api_key_id, api_key.concurrency_limit)
    
    return ConcurrencyStats(
        api_key_id=api_key_id,
        api_key_alias=api_key.alias,
        current=current,
        limit=limit,
        available=limit - current,
        provider_name=api_key.provider.name
    )


@router.put("/limits/{api_key_id}")
async def update_concurrency_limit(
    api_key_id: UUID,
    update: ConcurrencyLimitUpdate,
    db: Session = Depends(get_db)
) -> dict:
    """Update concurrency limit for a specific API key."""
    # Verify API key exists
    api_key = db.query(ApiKey).filter(ApiKey.id == api_key_id).first()
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")
    
    if update.limit < 1:
        raise HTTPException(status_code=400, detail="Limit must be at least 1")
    
    # Update in database
    api_key.concurrency_limit = update.limit
    db.commit()
    db.refresh(api_key)
    
    # Also update in runtime config (for immediate effect)
    manager = get_concurrency_manager()
    await manager.config.set_limit(api_key_id, update.limit)
    
    return {
        "api_key_id": api_key_id,
        "api_key_alias": api_key.alias,
        "new_limit": update.limit,
        "message": "Concurrency limit updated successfully"
    }


@router.delete("/limits/{api_key_id}")
async def reset_concurrency_limit(
    api_key_id: UUID,
    db: Session = Depends(get_db)
) -> dict:
    """Reset concurrency limit to default for a specific API key."""
    # Verify API key exists
    api_key = db.query(ApiKey).filter(ApiKey.id == api_key_id).first()
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")
    
    # Reset in database
    api_key.concurrency_limit = None
    db.commit()
    db.refresh(api_key)
    
    # Also remove from runtime config
    manager = get_concurrency_manager()
    await manager.config.remove_limit(api_key_id)
    default_limit = manager.config.default_limit
    
    return {
        "api_key_id": api_key_id,
        "api_key_alias": api_key.alias,
        "default_limit": default_limit,
        "message": "Concurrency limit reset to default"
    }


@router.get("/config")
async def get_concurrency_config() -> dict:
    """Get current concurrency configuration."""
    manager = get_concurrency_manager()
    
    return {
        "default_limit": manager.config.default_limit,
        "custom_limits_count": len(manager.config._custom_limits)
    }