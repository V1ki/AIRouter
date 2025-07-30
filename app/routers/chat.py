import json
import uuid
import logging
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Any, Dict
from openai import AsyncOpenAI

from app.db.database import get_db
from app.services import ModelService
from app.services.concurrency_manager import get_concurrency_manager

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)

router = APIRouter(prefix="/chat", tags=["Chat"])


def convert_chunk_to_response(chunk, model, conversation_id):
    """Convert an OpenAI chunk to a standardized response format."""
    response = chunk.model_dump()
    response["id"] = conversation_id
    response["model"] = model
    return response


@router.post("/completions")
async def chat_completions(
    body: Dict[str, Any],
    # Authorization: str = Header(None),
    db: Session = Depends(get_db),
):
    """Get completions for a prompt from a model."""
    logger.info(f"Received chat completion request:\n {json.dumps(body, indent=2, ensure_ascii=False)}")
    # get the model
    model = body.get("model")
    stream = body.get("stream", False)
    db_model = ModelService.get_model_by_name(db, name=model)
    if not db_model:
        return {"error": "Model not found"}, 404

    # get the Model implementations
    implementations = db_model.implementations

    # 使用新的方法获取最佳实现和API密钥，考虑并发限制
    best_implementation, db_api_key = await ModelService.get_best_implementation_with_concurrency(db, implementations)
    
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
    logger.info(f"Selected model: {model_id} provider: {provider.name} base_url: {base_url}")
    if stream:
        args["stream_options"] = {"include_usage": True}
    coversation_id = body.get("conversation_id", f"router-{uuid.uuid4()}")
    
    # Track the request with concurrency manager
    concurrency_manager = get_concurrency_manager()
    
    if stream:
        # For streaming, we need to handle concurrency tracking differently
        async def stream_generator():
            async with concurrency_manager.track_request(db_api_key.id):
                completion = await client.chat.completions.create(**args)
                async for chunk in completion:
                    data = convert_chunk_to_response(chunk, model, coversation_id)
                    usage = data.get("usage")
                    if usage:
                        ModelService.save_usage(db, db_api_key.id, best_implementation.id, usage)
                    
                    yield f"data: {json.dumps(data)}\n\n"
                yield "data: [DONE]\n\n"

        return StreamingResponse(
            content=stream_generator(), media_type="text/event-stream"
        )
    
    # For non-streaming requests
    async with concurrency_manager.track_request(db_api_key.id):
        completion = await client.chat.completions.create(**args)

    logger.debug(f"Completion response: {completion}")

    response = completion.model_dump()
    response["id"] = coversation_id
    response["model"] = model

    usage = response.get("usage")
    if usage:
        ModelService.save_usage(db, db_api_key.id, best_implementation.id, usage)
    logger.info(f"Final response for chat completion: {json.dumps(response, indent=2, ensure_ascii=False)}")
    return response
