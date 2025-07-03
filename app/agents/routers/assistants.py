from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from app.db.database import get_db
from app.agents.models import Assistant
from app.agents.services.assistant_service import AssistantService

router = APIRouter(prefix="/assistants", tags=["assistants"])


@router.post("")
async def create_assistant(
    model: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    instructions: Optional[str] = None,
    tools: Optional[List[Dict[str, Any]]] = None,
    file_ids: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db)
):
    """
    Create an assistant with a model and instructions.
    
    Args:
        model: ID of the model to use
        name: The name of the assistant
        description: The description of the assistant
        instructions: The system instructions that the assistant uses
        tools: A list of tool enabled on the assistant
        file_ids: A list of file IDs attached to this assistant
        metadata: Set of 16 key-value pairs for storing additional information
    
    Returns:
        The created assistant object
    """
    service = AssistantService(db)
    assistant = service.create_assistant(
        model=model,
        name=name,
        description=description,
        instructions=instructions,
        tools=tools or [],
        file_ids=file_ids or [],
        metadata=metadata or {}
    )
    return assistant.to_dict()


@router.get("")
async def list_assistants(
    limit: int = Query(20, ge=1, le=100),
    order: str = Query("desc", regex="^(asc|desc)$"),
    after: Optional[str] = None,
    before: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Returns a list of assistants.
    
    Args:
        limit: Maximum number of assistants to return
        order: Sort order by created_at timestamp
        after: Cursor for pagination (assistant ID)
        before: Cursor for pagination (assistant ID)
    
    Returns:
        A list of assistant objects
    """
    service = AssistantService(db)
    assistants = service.list_assistants(
        limit=limit,
        order=order,
        after=after,
        before=before
    )
    
    # Format response according to OpenAI API
    return {
        "object": "list",
        "data": [assistant.to_dict() for assistant in assistants],
        "first_id": assistants[0].id if assistants else None,
        "last_id": assistants[-1].id if assistants else None,
        "has_more": len(assistants) == limit
    }


@router.get("/{assistant_id}")
async def retrieve_assistant(
    assistant_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieves an assistant.
    
    Args:
        assistant_id: The ID of the assistant to retrieve
    
    Returns:
        The assistant object matching the specified ID
    """
    service = AssistantService(db)
    # Convert OpenAI style ID to UUID
    try:
        uuid_id = uuid.UUID(assistant_id.replace("asst_", "").replace("-", ""))
    except ValueError:
        raise HTTPException(status_code=404, detail="Assistant not found")
    
    assistant = service.get_assistant(uuid_id)
    if not assistant:
        raise HTTPException(status_code=404, detail="Assistant not found")
    
    return assistant.to_dict()


@router.post("/{assistant_id}")
async def modify_assistant(
    assistant_id: str,
    model: Optional[str] = None,
    name: Optional[str] = None,
    description: Optional[str] = None,
    instructions: Optional[str] = None,
    tools: Optional[List[Dict[str, Any]]] = None,
    file_ids: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db)
):
    """
    Modifies an assistant.
    
    Args:
        assistant_id: The ID of the assistant to modify
        model: ID of the model to use
        name: The name of the assistant
        description: The description of the assistant
        instructions: The system instructions that the assistant uses
        tools: A list of tool enabled on the assistant
        file_ids: A list of file IDs attached to this assistant
        metadata: Set of 16 key-value pairs for storing additional information
    
    Returns:
        The modified assistant object
    """
    service = AssistantService(db)
    # Convert OpenAI style ID to UUID
    try:
        uuid_id = uuid.UUID(assistant_id.replace("asst_", "").replace("-", ""))
    except ValueError:
        raise HTTPException(status_code=404, detail="Assistant not found")
    
    assistant = service.update_assistant(
        assistant_id=uuid_id,
        model=model,
        name=name,
        description=description,
        instructions=instructions,
        tools=tools,
        file_ids=file_ids,
        metadata=metadata
    )
    
    if not assistant:
        raise HTTPException(status_code=404, detail="Assistant not found")
    
    return assistant.to_dict()


@router.delete("/{assistant_id}")
async def delete_assistant(
    assistant_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete an assistant.
    
    Args:
        assistant_id: The ID of the assistant to delete
    
    Returns:
        Deletion status
    """
    service = AssistantService(db)
    # Convert OpenAI style ID to UUID
    try:
        uuid_id = uuid.UUID(assistant_id.replace("asst_", "").replace("-", ""))
    except ValueError:
        raise HTTPException(status_code=404, detail="Assistant not found")
    
    success = service.delete_assistant(uuid_id)
    if not success:
        raise HTTPException(status_code=404, detail="Assistant not found")
    
    return {
        "id": assistant_id,
        "object": "assistant.deleted",
        "deleted": True
    }