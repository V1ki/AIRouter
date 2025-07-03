from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from app.db.database import get_db
from app.agents.models import Thread, Message
from app.agents.services.thread_service import ThreadService
from app.agents.services.message_service import MessageService

router = APIRouter(prefix="/threads", tags=["threads"])


@router.post("")
async def create_thread(
    messages: Optional[List[Dict[str, Any]]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db)
):
    """
    Create a thread.
    
    Args:
        messages: A list of messages to start the thread with
        metadata: Set of 16 key-value pairs for storing additional information
    
    Returns:
        A thread object
    """
    service = ThreadService(db)
    thread = service.create_thread(metadata=metadata or {})
    
    # If initial messages are provided, create them
    if messages:
        message_service = MessageService(db)
        for msg_data in messages:
            message_service.create_message(
                thread_id=thread.id,
                role=msg_data.get("role"),
                content=msg_data.get("content"),
                file_ids=msg_data.get("file_ids", []),
                metadata=msg_data.get("metadata", {})
            )
    
    return thread.to_dict()


@router.get("/{thread_id}")
async def retrieve_thread(
    thread_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieves a thread.
    
    Args:
        thread_id: The ID of the thread to retrieve
    
    Returns:
        The thread object matching the specified ID
    """
    service = ThreadService(db)
    # Convert OpenAI style ID to UUID
    try:
        uuid_id = uuid.UUID(thread_id.replace("thread_", "").replace("-", ""))
    except ValueError:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    thread = service.get_thread(uuid_id)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    return thread.to_dict()


@router.post("/{thread_id}")
async def modify_thread(
    thread_id: str,
    metadata: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db)
):
    """
    Modifies a thread.
    
    Args:
        thread_id: The ID of the thread to modify
        metadata: Set of 16 key-value pairs for storing additional information
    
    Returns:
        The modified thread object
    """
    service = ThreadService(db)
    # Convert OpenAI style ID to UUID
    try:
        uuid_id = uuid.UUID(thread_id.replace("thread_", "").replace("-", ""))
    except ValueError:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    thread = service.update_thread(
        thread_id=uuid_id,
        metadata=metadata
    )
    
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    return thread.to_dict()


@router.delete("/{thread_id}")
async def delete_thread(
    thread_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a thread.
    
    Args:
        thread_id: The ID of the thread to delete
    
    Returns:
        Deletion status
    """
    service = ThreadService(db)
    # Convert OpenAI style ID to UUID
    try:
        uuid_id = uuid.UUID(thread_id.replace("thread_", "").replace("-", ""))
    except ValueError:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    success = service.delete_thread(uuid_id)
    if not success:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    return {
        "id": thread_id,
        "object": "thread.deleted",
        "deleted": True
    }