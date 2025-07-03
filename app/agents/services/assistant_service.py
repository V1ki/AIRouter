from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime

from app.agents.models import Assistant


class AssistantService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_assistant(
        self,
        model: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        instructions: Optional[str] = None,
        tools: List[Dict[str, Any]] = None,
        file_ids: List[str] = None,
        metadata: Dict[str, Any] = None,
        provider_id: Optional[uuid.UUID] = None
    ) -> Assistant:
        """Create a new assistant."""
        assistant = Assistant(
            model=model,
            name=name,
            description=description,
            instructions=instructions,
            tools=tools or [],
            file_ids=file_ids or [],
            metadata=metadata or {},
            provider_id=provider_id
        )
        
        self.db.add(assistant)
        self.db.commit()
        self.db.refresh(assistant)
        
        return assistant
    
    def get_assistant(self, assistant_id: uuid.UUID) -> Optional[Assistant]:
        """Get an assistant by ID."""
        return self.db.query(Assistant).filter(
            Assistant.id == assistant_id,
            Assistant.is_active == True
        ).first()
    
    def list_assistants(
        self,
        limit: int = 20,
        order: str = "desc",
        after: Optional[str] = None,
        before: Optional[str] = None
    ) -> List[Assistant]:
        """List assistants with pagination."""
        query = self.db.query(Assistant).filter(Assistant.is_active == True)
        
        # Apply cursor-based pagination
        if after:
            try:
                after_uuid = uuid.UUID(after.replace("asst_", "").replace("-", ""))
                after_assistant = self.get_assistant(after_uuid)
                if after_assistant:
                    if order == "desc":
                        query = query.filter(Assistant.created_at < after_assistant.created_at)
                    else:
                        query = query.filter(Assistant.created_at > after_assistant.created_at)
            except ValueError:
                pass
        
        if before:
            try:
                before_uuid = uuid.UUID(before.replace("asst_", "").replace("-", ""))
                before_assistant = self.get_assistant(before_uuid)
                if before_assistant:
                    if order == "desc":
                        query = query.filter(Assistant.created_at > before_assistant.created_at)
                    else:
                        query = query.filter(Assistant.created_at < before_assistant.created_at)
            except ValueError:
                pass
        
        # Apply ordering
        if order == "desc":
            query = query.order_by(desc(Assistant.created_at))
        else:
            query = query.order_by(asc(Assistant.created_at))
        
        # Apply limit
        return query.limit(limit).all()
    
    def update_assistant(
        self,
        assistant_id: uuid.UUID,
        model: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        instructions: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        file_ids: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Assistant]:
        """Update an assistant."""
        assistant = self.get_assistant(assistant_id)
        if not assistant:
            return None
        
        if model is not None:
            assistant.model = model
        if name is not None:
            assistant.name = name
        if description is not None:
            assistant.description = description
        if instructions is not None:
            assistant.instructions = instructions
        if tools is not None:
            assistant.tools = tools
        if file_ids is not None:
            assistant.file_ids = file_ids
        if metadata is not None:
            assistant.metadata = metadata
        
        self.db.commit()
        self.db.refresh(assistant)
        
        return assistant
    
    def delete_assistant(self, assistant_id: uuid.UUID) -> bool:
        """Soft delete an assistant."""
        assistant = self.get_assistant(assistant_id)
        if not assistant:
            return False
        
        assistant.is_active = False
        self.db.commit()
        
        return True