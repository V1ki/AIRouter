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

    args = {
        **body,
        "model": model_id,
    }
    if stream:
        args["stream_options"] = {"include_usage": True}
    coversation_id = body.get("conversation_id", f"router-{uuid.uuid4()}")
    completion = await client.chat.completions.create(**args)

    if stream:

        async def stream_generator():
            yield "event: start\n"
            yield 'data: {"model": "' + model + '"}\n\n'
            yield "event: model-response\n"

            async for chunk in completion:
                data = convert_chunk_to_response(chunk, model, coversation_id)
                usage = data.get("usage")
                if usage:
                    ModelService.save_usage(db, db_api_key.id,best_implementation.id, usage)
                
                yield f"data: {json.dumps(data)}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(
            content=stream_generator(), media_type="text/event-stream"
        )

    print(completion)

    response = completion.model_dump()
    response["id"] = coversation_id
    response["model"] = model

    usage = response.get("usage")
    if usage:
        ModelService.save_usage(db, db_api_key.id,best_implementation.id, usage)

    return response
