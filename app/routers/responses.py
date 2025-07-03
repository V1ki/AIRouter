from openai import AsyncOpenAI
import httpx
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services import ModelService
from typing import Any, Dict
import logging
import uuid

from app.services.response_service import ResponseService

router = APIRouter(prefix="/responses", tags=["Responses"])
# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)

@router.post("/")
async def create_response(
    body: Dict[str, Any],
    db: Session = Depends(get_db),
):
    logger.info(f"Received response request: {body}")
    model = body.get("model")
    stream = body.get("stream", False)
    db_model = ModelService.get_model_by_name(db, name=model)
    if not db_model:
        return {"error": "Model not found"}, 404
    
    # get the Model implementations
    implementations = db_model.implementations
    
    # 使用新的方法获取最佳实现和API密钥
    best_implementation, db_api_key = ModelService.get_best_implementation(db, implementations)
    
    if not best_implementation or not db_api_key:
        # 如果找不到合适的实现或API密钥，返回错误
        return {"error": "No suitable model implementation or API key available"}

    provider = best_implementation.provider
    api_key = db_api_key.key
    base_url = provider.base_url
    
    client = AsyncOpenAI(base_url=base_url, api_key=api_key)
    model_id = best_implementation.provider_model_id

    args = {
        **body,
        "model": model_id,
    }
    
    # 检查 base_url/responses 是否存在
    async with httpx.AsyncClient() as a:
        response = await a.post(f"{base_url}/responses", headers={
            "Authorization": f"Bearer {api_key}",
        })
        print(response.status_code)
        if response.status_code == 404:
            response = await ResponseService.handle_not_implements(db, client, args) 
            
            usage = response.get("usage")
            if usage:
                ModelService.save_usage(db, db_api_key.id, best_implementation.id, usage)

            return response
    

    logger.info(f"Selected model: {model_id} provider: {provider.name} base_url: {base_url}")
    if stream:
        return {"error": "Stream is not supported for responses"}
    
    response = await client.responses.create(**args)
    
    response["model"] = model

    usage = response.get("usage")
    if usage:
        ModelService.save_usage(db, db_api_key.id, best_implementation.id, usage)
    return response

@router.get("/{response_id}")
async def get_response(
    response_id: str,
    body: Dict[str, Any],
    db: Session = Depends(get_db),
):
    logger.info(f"Received response request: {response_id}, body: {body}")

    response = ResponseService.get_response(db, response_id)
    return response

@router.get("/{response_id}/input_items")
async def get_input_items(
    response_id: str,
    body: Dict[str, Any],   
    db: Session = Depends(get_db),
):
    logger.info(f"Received input_items request: {response_id}, body: {body}")
    items = ResponseService.get_response_input_items(db, response_id)
    
    items = [ {
        "id": item.id,
        "type" :"message",
        "role": item.role,
        "content": item.content,
    } for item in items ]
    
    return {
        "object": "list",
        "deleted": True,
        "has_more": False,
        "data": items,
    }



@router.delete("/{response_id}")
async def delete_response(
    response_id: str,
    db: Session = Depends(get_db),
):
    logger.info(f"Received response request: {response_id}")
    ResponseService.delete_response(db, response_id)
    return {
        'id': response_id,
        "object": "response",
        "deleted": True,
    }
