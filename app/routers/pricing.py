"""
Pricing management endpoints
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from datetime import datetime

from app.db.database import get_db
from app.models.provider import ModelImplementation
from app.services.litellm_pricing import (
    lookup_model_price,
    preview_sync,
    sync_prices_from_litellm,
    get_litellm_price_for_model,
    search_litellm_models,
)
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pricing", tags=["pricing"])

class PriceUpdate(BaseModel):
    model_id: str
    input_price: float
    output_price: float

class PriceBulkUpdate(BaseModel):
    prices: List[PriceUpdate]

class PriceResponse(BaseModel):
    model_id: str
    provider_model_id: str
    input_price: float
    output_price: float
    last_updated: Optional[datetime]
    updated_by: Optional[str]
    provider_name: str
    model_name: str

@router.get("/", response_model=List[PriceResponse])
def get_all_prices(
    skip: int = 0,
    limit: int = 1000,
    db: Session = Depends(get_db)
):
    """Get all model prices"""
    query = db.query(ModelImplementation).filter(
        ModelImplementation.pricing_info.isnot(None)
    ).offset(skip).limit(limit)
    
    results = []
    for impl in query.all():
        if impl.pricing_info:
            results.append(PriceResponse(
                model_id=str(impl.id),
                provider_model_id=impl.provider_model_id,
                input_price=float(impl.pricing_info.get('input_price', 0)),
                output_price=float(impl.pricing_info.get('output_price', 0)),
                last_updated=impl.pricing_info.get('last_updated'),
                updated_by=impl.pricing_info.get('updated_by'),
                provider_name=impl.provider.name,
                model_name=impl.model.name
            ))
    
    return results

@router.get("/model/{model_id}")
def get_model_price(
    model_id: str,
    db: Session = Depends(get_db)
):
    """Get price for a specific model implementation"""
    impl = db.query(ModelImplementation).filter(
        ModelImplementation.id == model_id
    ).first()
    
    if not impl:
        raise HTTPException(status_code=404, detail="Model implementation not found")
    
    if not impl.pricing_info:
        raise HTTPException(status_code=404, detail="No pricing information available")
    
    return PriceResponse(
        model_id=str(impl.id),
        provider_model_id=impl.provider_model_id,
        input_price=float(impl.pricing_info.get('input_price', 0)),
        output_price=float(impl.pricing_info.get('output_price', 0)),
        last_updated=impl.pricing_info.get('last_updated'),
        updated_by=impl.pricing_info.get('updated_by'),
        provider_name=impl.provider.name,
        model_name=impl.model.name
    )

@router.put("/model/{model_id}")
def update_model_price(
    model_id: str,
    price: PriceUpdate,
    db: Session = Depends(get_db)
):
    """Update price for a specific model"""
    impl = db.query(ModelImplementation).filter(
        ModelImplementation.id == model_id
    ).first()
    
    if not impl:
        raise HTTPException(status_code=404, detail="Model implementation not found")
    
    # Update pricing info
    pricing_info = impl.pricing_info or {}
    pricing_info['input_price'] = price.input_price
    pricing_info['output_price'] = price.output_price
    pricing_info['last_updated'] = datetime.utcnow().isoformat()
    pricing_info['updated_by'] = 'manual'
    
    impl.pricing_info = pricing_info
    db.commit()
    
    return {"message": "Price updated successfully", "model_id": model_id}

@router.post("/bulk-update")
def bulk_update_prices(
    updates: PriceBulkUpdate,
    db: Session = Depends(get_db)
):
    """Bulk update multiple model prices"""
    updated_count = 0
    errors = []
    
    for price_update in updates.prices:
        try:
            impl = db.query(ModelImplementation).filter(
                ModelImplementation.provider_model_id == price_update.model_id
            ).first()
            
            if impl:
                pricing_info = impl.pricing_info or {}
                pricing_info['input_price'] = price_update.input_price
                pricing_info['output_price'] = price_update.output_price
                pricing_info['last_updated'] = datetime.utcnow().isoformat()
                pricing_info['updated_by'] = 'bulk_update'
                
                impl.pricing_info = pricing_info
                updated_count += 1
            else:
                errors.append(f"Model {price_update.model_id} not found")
                
        except Exception as e:
            errors.append(f"Failed to update {price_update.model_id}: {str(e)}")
    
    db.commit()
    
    return {
        "updated_count": updated_count,
        "errors": errors,
        "success": len(errors) == 0
    }


@router.get("/comparison")
def get_price_comparison(
    model_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get price comparison across providers for similar models"""
    query = db.query(ModelImplementation).filter(
        ModelImplementation.pricing_info.isnot(None)
    )
    
    if model_type:
        query = query.join(ModelImplementation.model).filter(
            ModelImplementation.model.has(family=model_type)
        )
    
    results = {}
    for impl in query.all():
        if impl.pricing_info:
            model_family = impl.model.family
            if model_family not in results:
                results[model_family] = []
            
            results[model_family].append({
                "provider": impl.provider.name,
                "model": impl.model.name,
                "provider_model_id": impl.provider_model_id,
                "input_price": float(impl.pricing_info.get('input_price', 0)),
                "output_price": float(impl.pricing_info.get('output_price', 0)),
                "context_window": impl.context_window
            })
    
    # Sort by price within each family
    for family in results:
        results[family].sort(key=lambda x: x['input_price'])

    return results


# ==================== LiteLLM Pricing Endpoints ====================

@router.get("/litellm/preview")
def preview_litellm_sync(
    db: Session = Depends(get_db)
):
    """
    Preview what prices would change if synced from LiteLLM.

    Returns a list of all model implementations with their current prices
    and what LiteLLM would set them to, without making any changes.
    """
    results = preview_sync(db)

    matched = [r for r in results if r["has_litellm_price"]]
    changed = [r for r in results if r["price_changed"]]
    not_found = [r for r in results if not r["has_litellm_price"]]

    return {
        "total_models": len(results),
        "matched_in_litellm": len(matched),
        "would_change": len(changed),
        "not_found_in_litellm": len(not_found),
        "details": results,
    }


@router.post("/litellm/sync")
def sync_from_litellm(
    only_missing: bool = Query(False, description="Only update models without existing pricing"),
    provider: Optional[str] = Query(None, description="Filter by provider name"),
    db: Session = Depends(get_db)
):
    """
    Sync model prices from LiteLLM's pricing database.

    LiteLLM maintains pricing data for 2500+ models. This endpoint updates
    the pricing_info for all matching model implementations.

    Query parameters:
    - only_missing: If true, only fills in prices for models that don't have any yet
    - provider: Optional provider name to limit sync to a specific provider
    """
    result = sync_prices_from_litellm(db, only_missing=only_missing, provider_filter=provider)
    logger.info(
        f"LiteLLM pricing sync: updated={result['updated_count']}, "
        f"skipped={result['skipped_count']}, not_found={result['not_found_count']}"
    )
    return result


@router.get("/litellm/lookup/{provider_model_id:path}")
def lookup_litellm_price(
    provider_model_id: str,
    provider_name: Optional[str] = Query(None, description="Provider name for better matching"),
):
    """
    Look up a single model's pricing from LiteLLM.

    Useful for checking pricing before adding a new model implementation.
    Does not modify any data.
    """
    result = get_litellm_price_for_model(provider_model_id, provider_name)

    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"Model '{provider_model_id}' not found in LiteLLM pricing database"
        )

    return {
        "provider_model_id": provider_model_id,
        "provider_name": provider_name,
        "pricing": result,
    }


@router.get("/litellm/models")
def list_litellm_models(
    search: str = Query("", description="Search query to filter model IDs"),
    provider_name: Optional[str] = Query(None, description="Filter by provider name"),
    limit: int = Query(50, description="Maximum number of results", ge=1, le=200),
):
    """
    Search available models from LiteLLM's pricing database.

    Used by the frontend to populate autocomplete for model selection.
    Returns model IDs with pricing info for the given provider/search query.
    """
    results = search_litellm_models(search=search, provider_name=provider_name, limit=limit)
    return {
        "count": len(results),
        "models": results,
    }