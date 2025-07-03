from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import uuid

from app.db.database import get_db
from app.agents.models import Message, MessageRole
from app.agents.services.message_service import MessageService

router = APIRouter(tags=["messages"])


@router.post("/threads/{thread_id}/messages")
async def create_message(
    thread_id: str,
    role: str,
    content: List[Dict[str, Any]],
    file_ids: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db)
):
    """
    Create a message within a thread.
    
    Args:
        thread_id: The ID of the thread to create a message for
        role: The role of the entity that is creating the message (user or assistant)
        content: The content of the message in array format
        file_ids: A list of File IDs that the message should use
        metadata: Set of 16 key-value pairs for storing additional information
    
    Returns:
        A message object
    """
    service = MessageService(db)
    
    # Convert OpenAI style thread ID to UUID
    try:
        thread_uuid = uuid.UUID(thread_id.replace("thread_", "").replace("-", ""))
    except ValueError:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    # Validate role
    try:
        role_enum = MessageRole(role)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid role: {role}")
    
    message = service.create_message(
        thread_id=thread_uuid,
        role=role_enum,
        content=content,
        file_ids=file_ids or [],
        metadata=metadata or {}
    )
    
    if not message:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    return message.to_dict()


@router.get("/threads/{thread_id}/messages")
async def list_messages(
    thread_id: str,
    limit: int = Query(20, ge=1, le=100),
    order: str = Query("desc", regex="^(asc|desc)$"),
    after: Optional[str] = None,
    before: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Returns a list of messages for a given thread.
    
    Args:
        thread_id: The ID of the thread the messages belong to
        limit: Maximum number of messages to return
        order: Sort order by created_at timestamp
        after: Cursor for pagination (message ID)
        before: Cursor for pagination (message ID)
    
    Returns:
        A list of message objects
    """
    service = MessageService(db)
    
    # Convert OpenAI style thread ID to UUID
    try:
        thread_uuid = uuid.UUID(thread_id.replace("thread_", "").replace("-", ""))
    except ValueError:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    messages = service.list_messages(
        thread_id=thread_uuid,
        limit=limit,
        order=order,
        after=after,
        before=before
    )
    
    # Format response according to OpenAI API
    return {
        "object": "list",
        "data": [message.to_dict() for message in messages],
        "first_id": messages[0].id if messages else None,
        "last_id": messages[-1].id if messages else None,
        "has_more": len(messages) == limit
    }


@router.get("/threads/{thread_id}/messages/{message_id}")
async def retrieve_message(
    thread_id: str,
    message_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieve a message.
    
    Args:
        thread_id: The ID of the thread to which this message belongs
        message_id: The ID of the message to retrieve
    
    Returns:
        The message object matching the specified ID
    """
    service = MessageService(db)
    
    # Convert OpenAI style IDs to UUIDs
    try:
        thread_uuid = uuid.UUID(thread_id.replace("thread_", "").replace("-", ""))
        message_uuid = uuid.UUID(message_id.replace("msg_", "").replace("-", ""))
    except ValueError:
        raise HTTPException(status_code=404, detail="Message not found")
    
    message = service.get_message(message_uuid, thread_uuid)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    return message.to_dict()


@router.post("/threads/{thread_id}/messages/{message_id}")
async def modify_message(
    thread_id: str,
    message_id: str,
    metadata: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db)
):
    """
    Modifies a message.
    
    Args:
        thread_id: The ID of the thread to which this message belongs
        message_id: The ID of the message to modify
        metadata: Set of 16 key-value pairs for storing additional information
    
    Returns:
        The modified message object
    """
    service = MessageService(db)
    
    # Convert OpenAI style IDs to UUIDs
    try:
        thread_uuid = uuid.UUID(thread_id.replace("thread_", "").replace("-", ""))
        message_uuid = uuid.UUID(message_id.replace("msg_", "").replace("-", ""))
    except ValueError:
        raise HTTPException(status_code=404, detail="Message not found")
    
    message = service.update_message(
        message_id=message_uuid,
        thread_id=thread_uuid,
        metadata=metadata
    )
    
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    return message.to_dict()