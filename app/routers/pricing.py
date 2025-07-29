"""
Pricing management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from datetime import datetime

from app.db.database import get_db
from app.models.provider import ModelImplementation
from pydantic import BaseModel

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