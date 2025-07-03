from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, and_
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime

from app.agents.models import Message, MessageRole, MessageStatus, Thread
from app.agents.services.thread_service import ThreadService


class MessageService:
    def __init__(self, db: Session):
        self.db = db
        self.thread_service = ThreadService(db)
    
    def create_message(
        self,
        thread_id: uuid.UUID,
        role: MessageRole,
        content: List[Dict[str, Any]],
        file_ids: List[str] = None,
        metadata: Dict[str, Any] = None,
        assistant_id: Optional[uuid.UUID] = None,
        run_id: Optional[uuid.UUID] = None
    ) -> Optional[Message]:
        """Create a new message in a thread."""
        # Verify thread exists
        thread = self.thread_service.get_thread(thread_id)
        if not thread:
            return None
        
        message = Message(
            thread_id=thread_id,
            role=role,
            content=content,
            file_ids=file_ids or [],
            metadata=metadata or {},
            assistant_id=assistant_id,
            run_id=run_id,
            status=MessageStatus.COMPLETED,
            completed_at=datetime.utcnow()
        )
        
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        
        # Update thread's last message time
        self.thread_service.update_last_message_time(thread_id)
        
        return message
    
    def get_message(
        self,
        message_id: uuid.UUID,
        thread_id: uuid.UUID
    ) -> Optional[Message]:
        """Get a message by ID and thread ID."""
        return self.db.query(Message).filter(
            and_(
                Message.id == message_id,
                Message.thread_id == thread_id
            )
        ).first()
    
    def list_messages(
        self,
        thread_id: uuid.UUID,
        limit: int = 20,
        order: str = "desc",
        after: Optional[str] = None,
        before: Optional[str] = None
    ) -> List[Message]:
        """List messages in a thread with pagination."""
        query = self.db.query(Message).filter(Message.thread_id == thread_id)
        
        # Apply cursor-based pagination
        if after:
            try:
                after_uuid = uuid.UUID(after.replace("msg_", "").replace("-", ""))
                after_message = self.db.query(Message).filter(
                    Message.id == after_uuid
                ).first()
                if after_message:
                    if order == "desc":
                        query = query.filter(Message.created_at < after_message.created_at)
                    else:
                        query = query.filter(Message.created_at > after_message.created_at)
            except ValueError:
                pass
        
        if before:
            try:
                before_uuid = uuid.UUID(before.replace("msg_", "").replace("-", ""))
                before_message = self.db.query(Message).filter(
                    Message.id == before_uuid
                ).first()
                if before_message:
                    if order == "desc":
                        query = query.filter(Message.created_at > before_message.created_at)
                    else:
                        query = query.filter(Message.created_at < before_message.created_at)
            except ValueError:
                pass
        
        # Apply ordering
        if order == "desc":
            query = query.order_by(desc(Message.created_at))
        else:
            query = query.order_by(asc(Message.created_at))
        
        # Apply limit
        return query.limit(limit).all()
    
    def update_message(
        self,
        message_id: uuid.UUID,
        thread_id: uuid.UUID,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Message]:
        """Update a message's metadata."""
        message = self.get_message(message_id, thread_id)
        if not message:
            return None
        
        if metadata is not None:
            message.metadata = metadata
        
        self.db.commit()
        self.db.refresh(message)
        
        return message
    
    def mark_message_incomplete(
        self,
        message_id: uuid.UUID,
        reason: str
    ) -> Optional[Message]:
        """Mark a message as incomplete."""
        message = self.db.query(Message).filter(
            Message.id == message_id
        ).first()
        if not message:
            return None
        
        message.status = MessageStatus.INCOMPLETE
        message.incomplete_at = datetime.utcnow()
        message.incomplete_details = {"reason": reason}
        
        self.db.commit()
        self.db.refresh(message)
        
        return message