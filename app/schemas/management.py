from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

from app.models.provider import FreeQuotaType, ResetPeriod

# Provider schemas
class ProviderBase(BaseModel):
    name: str
    base_url: str
    description: Optional[str] = None
    free_quota_type: Optional[FreeQuotaType] = None

class ProviderCreate(ProviderBase):
    pass

class ProviderUpdate(BaseModel):
    name: Optional[str] = None
    base_url: Optional[str] = None
    description: Optional[str] = None
    free_quota_type: Optional[FreeQuotaType] = None

class ProviderResponse(ProviderBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID

# API Key schemas
class ApiKeyBase(BaseModel):
    provider_id: UUID
    alias: str
    key: str
    sort_order: Optional[int] = 0
    concurrency_limit: Optional[int] = None

class ApiKeyCreate(ApiKeyBase):
    pass

class ApiKeyUpdate(BaseModel):
    alias: Optional[str] = None
    key: Optional[str] = None
    sort_order: Optional[int] = None
    concurrency_limit: Optional[int] = None

class ApiKeyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    provider_id: UUID
    alias: str
    key: str
    sort_order: Optional[int] = 0
    concurrency_limit: Optional[int] = None

# Model schemas
class ModelBase(BaseModel):
    name: str
    description: Optional[str] = None
    capabilities: List[str]
    family: str

class ModelCreate(ModelBase):
    pass

class ModelUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    capabilities: Optional[List[str]] = None
    family: Optional[str] = None

class ModelResponse(ModelBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID

# Model Implementation schemas
class ModelImplementationBase(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    provider_id: UUID
    model_id: UUID
    provider_model_id: str
    version: Optional[str] = None
    context_window: Optional[int] = None
    pricing_info: Optional[Dict[str, Any]] = None
    is_available: bool = True
    custom_parameters: Optional[Dict[str, Any]] = None
    sort_order: int = 0

class ModelImplementationCreate(ModelImplementationBase):
    model_config = ConfigDict(protected_namespaces=())

class ModelImplementationUpdate(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    provider_model_id: Optional[str] = None
    version: Optional[str] = None
    context_window: Optional[int] = None
    pricing_info: Optional[Dict[str, Any]] = None
    is_available: Optional[bool] = None
    custom_parameters: Optional[Dict[str, Any]] = None
    sort_order: Optional[int] = None

class ModelImplementationResponse(ModelImplementationBase):
    model_config = ConfigDict(protected_namespaces=(), from_attributes=True)
    
    id: UUID

# Quick-add model schema (creates Model + first Implementation atomically)
class ModelQuickAddRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    # Model fields
    name: str
    description: Optional[str] = None
    capabilities: List[str] = []
    family: str

    # Implementation fields
    provider_id: UUID
    provider_model_id: str
    version: Optional[str] = None
    context_window: Optional[int] = None
    pricing_info: Optional[Dict[str, Any]] = None
    is_available: bool = True
    sort_order: int = 0


class ModelQuickAddResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=(), from_attributes=True)

    model: ModelResponse
    implementation: ModelImplementationResponse


# Usage statistics schemas - removed UsageStatsResponse since we return array directly

class UsageResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=(), from_attributes=True)
    
    id: UUID
    api_key_id: UUID
    model_implementation_id: UUID
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    prompt_tokens_details: Optional[Dict[str, Any]] = None
    completion_tokens_details: Optional[Dict[str, Any]] = None
    timestamp: datetime