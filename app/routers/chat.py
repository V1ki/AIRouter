import json
import uuid
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Any, Dict, List
from openai import AsyncOpenAI
from openai.types.model import Model

import time
from app.db.database import get_db
from app.services import ModelService

router = APIRouter(prefix="/chat", tags=["Chat"])


def convert_chunk_to_response(chunk, model, conversation_id):
    """Convert an OpenAI chunk to a standardized response format."""
    choices = []
    for choice in chunk.choices:
        delta = {}
        for attr in ["content", "role", "tool_calls", "reasoning_content"]:
            if hasattr(choice.delta, attr) and getattr(choice.delta, attr) is not None:
                delta[attr] = getattr(choice.delta, attr)
        
        choice_data = {
            "delta": delta,
            "index": choice.index,
            "finish_reason": choice.finish_reason,
        }
        
        if hasattr(choice, "logprobs") and choice.logprobs is not None:
            choice_data["logprobs"] = choice.logprobs
            
        choices.append(choice_data)
    
    response = {
        "id": conversation_id,
        "object": chunk.object,
        "created": chunk.created,
        "model": model,  # Use the original model name
        "choices": choices,
        "system_fingerprint": chunk.system_fingerprint if hasattr(chunk, "system_fingerprint") else None,
    }
    
    if hasattr(chunk, "usage") and chunk.usage is not None:
        response["usage"] = chunk.usage
        
    return response


@router.post("/completions")
async def chat_completions(
    body: Dict[str, Any],
    # Authorization: str = Header(None),
    db: Session = Depends(get_db),
):
    """Get completions for a prompt from a model."""
    print(body)
    # get the model
    model = body.get("model")
    stream = body.get("stream", False)
    db_model = ModelService.get_model_by_name(db, name=model)

    # get the Model implementations
    implementations = db_model.implementations

    # TODO: find the best implementation
    best_implementation = implementations[0]

    provider = best_implementation.provider

    # TODO: find the best API key
    db_api_key = provider.api_keys[0]
    api_key = db_api_key.key
    base_url = provider.base_url

    client = AsyncOpenAI(base_url=base_url, api_key=api_key)

    model_id = best_implementation.provider_model_id

    args = {**body, "model": model_id}
    coversation_id = body.get("conversation_id", f"router-{uuid.uuid4()}")
    completion = await client.chat.completions.create(**args)

    if stream:

        async def stream_generator():
            yield "event: start\n"
            yield 'data: {"model": "' + model + '"}\n\n'
            yield "event: model-response\n"

            async for chunk in completion:
                data = convert_chunk_to_response(chunk, model, coversation_id)
                yield f"data: {json.dumps(data)}\n\n"

        return StreamingResponse(
            content=stream_generator(), media_type="text/event-stream"
        )

    print(completion)
    return {
        "id": coversation_id,
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "usage": completion.usage,
        "choices": completion.choices,
    }
