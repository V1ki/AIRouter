from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from openai.types.model import Model

import time
from app.db.database import get_db
from app.services.model_service import ModelService
from openai.pagination import SyncPage

router = APIRouter(prefix="/models", tags=["models"])

@router.get("/", response_model=SyncPage[Model])
def get_models(
    db: Session = Depends(get_db)
):
    """Get all models with pagination and implementation counts."""
    db_models = ModelService.get_models(db)
    models = []
    for db_model in db_models:
        if len(db_model.implementations) == 0:
            continue
        model = Model(
            id=db_model.name,
            created=int(time.time()),
            object="model",
            owned_by=db_model.family,
        )
        models.append(model)
    return {
        "object": "list",
        "data": models
    }

