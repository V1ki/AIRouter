from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from datetime import datetime, date
from uuid import UUID

from app.db.database import get_db
from app.models.provider import (
    ModelProvider, ApiKey, Model, ModelImplementation, 
    ApiKeyUsage, FreeQuotaType, ResetPeriod
)
from app.schemas.management import (
    ProviderCreate, ProviderUpdate, ProviderResponse,
    ApiKeyCreate, ApiKeyUpdate, ApiKeyResponse,
    ModelCreate, ModelUpdate, ModelResponse,
    ModelImplementationCreate, ModelImplementationUpdate, ModelImplementationResponse,
    UsageResponse
)

router = APIRouter(prefix="/api", tags=["management"])

# Provider CRUD endpoints
@router.get("/providers", response_model=List[ProviderResponse])
def get_providers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all providers with pagination."""
    providers = db.query(ModelProvider).offset(skip).limit(limit).all()
    return providers

@router.post("/providers", response_model=ProviderResponse)
def create_provider(
    provider: ProviderCreate,
    db: Session = Depends(get_db)
):
    """Create a new provider."""
    try:
        db_provider = ModelProvider(**provider.dict())
        db.add(db_provider)
        db.commit()
        db.refresh(db_provider)
        return db_provider
    except IntegrityError as e:
        db.rollback()
        if "unique constraint" in str(e).lower() and "base_url" in str(e).lower():
            raise HTTPException(
                status_code=400, 
                detail=f"Provider with base_url '{provider.base_url}' already exists"
            )
        raise HTTPException(status_code=400, detail="Failed to create provider")

@router.put("/providers/{provider_id}", response_model=ProviderResponse)
def update_provider(
    provider_id: UUID,
    provider: ProviderUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing provider."""
    db_provider = db.query(ModelProvider).filter(ModelProvider.id == provider_id).first()
    if not db_provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    try:
        update_data = provider.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_provider, field, value)
        
        db.commit()
        db.refresh(db_provider)
        return db_provider
    except IntegrityError as e:
        db.rollback()
        if "unique constraint" in str(e).lower() and "base_url" in str(e).lower():
            raise HTTPException(
                status_code=400, 
                detail=f"Provider with base_url '{provider.base_url}' already exists"
            )
        raise HTTPException(status_code=400, detail="Failed to update provider")

@router.delete("/providers/{provider_id}")
def delete_provider(
    provider_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a provider."""
    db_provider = db.query(ModelProvider).filter(ModelProvider.id == provider_id).first()
    if not db_provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    db.delete(db_provider)
    db.commit()
    return {"message": "Provider deleted successfully"}

# API Key CRUD endpoints
@router.get("/api-keys", response_model=List[ApiKeyResponse])
def get_api_keys(
    provider_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all API keys with optional provider filter."""
    query = db.query(ApiKey)
    if provider_id:
        query = query.filter(ApiKey.provider_id == provider_id)
    
    api_keys = query.offset(skip).limit(limit).all()
    return api_keys

@router.post("/api-keys", response_model=ApiKeyResponse)
def create_api_key(
    api_key: ApiKeyCreate,
    db: Session = Depends(get_db)
):
    """Create a new API key."""
    # Verify provider exists
    provider = db.query(ModelProvider).filter(ModelProvider.id == api_key.provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    # Validate API key
    if not api_key.key or api_key.key.strip() == "":
        raise HTTPException(status_code=400, detail="API key cannot be empty")
    
    if not api_key.alias or api_key.alias.strip() == "":
        raise HTTPException(status_code=400, detail="API key alias cannot be empty")
    
    db_api_key = ApiKey(**api_key.dict())
    db.add(db_api_key)
    db.commit()
    db.refresh(db_api_key)
    return db_api_key

@router.put("/api-keys/{api_key_id}", response_model=ApiKeyResponse)
def update_api_key(
    api_key_id: UUID,
    api_key: ApiKeyUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing API key."""
    db_api_key = db.query(ApiKey).filter(ApiKey.id == api_key_id).first()
    if not db_api_key:
        raise HTTPException(status_code=404, detail="API key not found")
    
    update_data = api_key.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_api_key, field, value)
    
    db.commit()
    db.refresh(db_api_key)
    return db_api_key

@router.delete("/api-keys/{api_key_id}")
def delete_api_key(
    api_key_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete an API key."""
    db_api_key = db.query(ApiKey).filter(ApiKey.id == api_key_id).first()
    if not db_api_key:
        raise HTTPException(status_code=404, detail="API key not found")
    
    db.delete(db_api_key)
    db.commit()
    return {"message": "API key deleted successfully"}

# Model CRUD endpoints
@router.get("/models", response_model=List[ModelResponse])
def get_models(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all models with pagination."""
    models = db.query(Model).offset(skip).limit(limit).all()
    return models

@router.post("/models", response_model=ModelResponse)
def create_model(
    model: ModelCreate,
    db: Session = Depends(get_db)
):
    """Create a new model."""
    db_model = Model(**model.dict())
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model

@router.put("/models/{model_id}", response_model=ModelResponse)
def update_model(
    model_id: UUID,
    model: ModelUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing model."""
    db_model = db.query(Model).filter(Model.id == model_id).first()
    if not db_model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    update_data = model.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_model, field, value)
    
    db.commit()
    db.refresh(db_model)
    return db_model

@router.delete("/models/{model_id}")
def delete_model(
    model_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a model."""
    db_model = db.query(Model).filter(Model.id == model_id).first()
    if not db_model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    db.delete(db_model)
    db.commit()
    return {"message": "Model deleted successfully"}

# Model Implementation CRUD endpoints
@router.get("/model-implementations", response_model=List[ModelImplementationResponse])
def get_model_implementations(
    provider_id: Optional[UUID] = None,
    model_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all model implementations with optional filters."""
    query = db.query(ModelImplementation)
    if provider_id:
        query = query.filter(ModelImplementation.provider_id == provider_id)
    if model_id:
        query = query.filter(ModelImplementation.model_id == model_id)
    
    implementations = query.offset(skip).limit(limit).all()
    return implementations

@router.post("/model-implementations", response_model=ModelImplementationResponse)
def create_model_implementation(
    implementation: ModelImplementationCreate,
    db: Session = Depends(get_db)
):
    """Create a new model implementation."""
    # Verify provider and model exist
    provider = db.query(ModelProvider).filter(ModelProvider.id == implementation.provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    model = db.query(Model).filter(Model.id == implementation.model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    db_implementation = ModelImplementation(**implementation.dict())
    db.add(db_implementation)
    db.commit()
    db.refresh(db_implementation)
    return db_implementation

@router.put("/model-implementations/{implementation_id}", response_model=ModelImplementationResponse)
def update_model_implementation(
    implementation_id: UUID,
    implementation: ModelImplementationUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing model implementation."""
    db_implementation = db.query(ModelImplementation).filter(ModelImplementation.id == implementation_id).first()
    if not db_implementation:
        raise HTTPException(status_code=404, detail="Model implementation not found")
    
    update_data = implementation.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_implementation, field, value)
    
    db.commit()
    db.refresh(db_implementation)
    return db_implementation

@router.delete("/model-implementations/{implementation_id}")
def delete_model_implementation(
    implementation_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a model implementation."""
    db_implementation = db.query(ModelImplementation).filter(ModelImplementation.id == implementation_id).first()
    if not db_implementation:
        raise HTTPException(status_code=404, detail="Model implementation not found")
    
    db.delete(db_implementation)
    db.commit()
    return {"message": "Model implementation deleted successfully"}

# Usage statistics endpoints
@router.get("/usage/stats")
def get_usage_stats(
    start_date: Optional[date] = Query(None, description="Start date for filtering"),
    end_date: Optional[date] = Query(None, description="End date for filtering"),
    group_by: Optional[str] = Query("day", description="Group by: day, week, month, provider, model"),
    db: Session = Depends(get_db)
):
    """Get aggregated usage statistics."""
    from sqlalchemy import func
    
    # Validate group_by parameter
    valid_group_by = ["day", "week", "month", "provider", "model"]
    if group_by not in valid_group_by:
        raise HTTPException(status_code=400, detail=f"Invalid group_by value. Must be one of: {', '.join(valid_group_by)}")
    
    # For provider/model grouping, we need different queries
    if group_by == "provider":
        query = db.query(
            ModelProvider.name.label('group_name'),
            func.sum(ApiKeyUsage.prompt_tokens).label('total_prompt_tokens'),
            func.sum(ApiKeyUsage.completion_tokens).label('total_completion_tokens'),
            func.sum(ApiKeyUsage.total_tokens).label('total_tokens'),
            func.count(ApiKeyUsage.id).label('request_count')
        ).join(
            ApiKey, ApiKeyUsage.api_key_id == ApiKey.id
        ).join(
            ModelProvider, ApiKey.provider_id == ModelProvider.id
        )
        
        if start_date:
            query = query.filter(ApiKeyUsage.timestamp >= start_date)
        if end_date:
            query = query.filter(ApiKeyUsage.timestamp <= end_date)
        
        stats = query.group_by(ModelProvider.name).order_by(ModelProvider.name).all()
        
        # Return array directly (frontend expects array, not object with stats key)
        return [
            {
                "group_name": stat.group_name,
                "total_prompt_tokens": stat.total_prompt_tokens or 0,
                "total_completion_tokens": stat.total_completion_tokens or 0,
                "total_tokens": stat.total_tokens or 0,
                "request_count": stat.request_count or 0
            }
            for stat in stats
        ]
    
    elif group_by == "model":
        query = db.query(
            Model.name.label('group_name'),
            func.sum(ApiKeyUsage.prompt_tokens).label('total_prompt_tokens'),
            func.sum(ApiKeyUsage.completion_tokens).label('total_completion_tokens'),
            func.sum(ApiKeyUsage.total_tokens).label('total_tokens'),
            func.count(ApiKeyUsage.id).label('request_count')
        ).join(
            ModelImplementation, ApiKeyUsage.model_implementation_id == ModelImplementation.id
        ).join(
            Model, ModelImplementation.model_id == Model.id
        )
        
        if start_date:
            query = query.filter(ApiKeyUsage.timestamp >= start_date)
        if end_date:
            query = query.filter(ApiKeyUsage.timestamp <= end_date)
        
        stats = query.group_by(Model.name).order_by(Model.name).all()
        
        # Return array directly
        return [
            {
                "group_name": stat.group_name,
                "total_prompt_tokens": stat.total_prompt_tokens or 0,
                "total_completion_tokens": stat.total_completion_tokens or 0,
                "total_tokens": stat.total_tokens or 0,
                "request_count": stat.request_count or 0
            }
            for stat in stats
        ]
    
    else:
        # Time-based grouping (day, week, month)
        query = db.query(
            func.date_trunc(group_by, ApiKeyUsage.timestamp).label('period'),
            func.sum(ApiKeyUsage.prompt_tokens).label('total_prompt_tokens'),
            func.sum(ApiKeyUsage.completion_tokens).label('total_completion_tokens'),
            func.sum(ApiKeyUsage.total_tokens).label('total_tokens'),
            func.count(ApiKeyUsage.id).label('request_count')
        )
        
        if start_date:
            query = query.filter(ApiKeyUsage.timestamp >= start_date)
        if end_date:
            query = query.filter(ApiKeyUsage.timestamp <= end_date)
        
        stats = query.group_by('period').order_by('period').all()
        
        # Return array directly
        return [
            {
                "period": stat.period.isoformat() if stat.period else None,
                "total_prompt_tokens": stat.total_prompt_tokens or 0,
                "total_completion_tokens": stat.total_completion_tokens or 0,
                "total_tokens": stat.total_tokens or 0,
                "request_count": stat.request_count or 0
            }
            for stat in stats
        ]

@router.get("/usage", response_model=List[UsageResponse])
def get_usage(
    start_date: Optional[datetime] = Query(None, description="Start date for filtering"),
    end_date: Optional[datetime] = Query(None, description="End date for filtering"),
    api_key_id: Optional[UUID] = Query(None, description="Filter by API key"),
    model_implementation_id: Optional[UUID] = Query(None, description="Filter by model implementation"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get detailed usage records."""
    query = db.query(ApiKeyUsage)
    
    if start_date:
        query = query.filter(ApiKeyUsage.timestamp >= start_date)
    if end_date:
        query = query.filter(ApiKeyUsage.timestamp <= end_date)
    if api_key_id:
        query = query.filter(ApiKeyUsage.api_key_id == api_key_id)
    if model_implementation_id:
        query = query.filter(ApiKeyUsage.model_implementation_id == model_implementation_id)
    
    usage_records = query.order_by(ApiKeyUsage.timestamp.desc()).offset(skip).limit(limit).all()
    return usage_records