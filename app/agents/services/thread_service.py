from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import uuid
from datetime import datetime

from app.agents.models import Thread


class ThreadService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_thread(
        self,
        metadata: Dict[str, Any] = None
    ) -> Thread:
        """Create a new thread."""
        thread = Thread(
            metadata=metadata or {}
        )
        
        self.db.add(thread)
        self.db.commit()
        self.db.refresh(thread)
        
        return thread
    
    def get_thread(self, thread_id: uuid.UUID) -> Optional[Thread]:
        """Get a thread by ID."""
        return self.db.query(Thread).filter(
            Thread.id == thread_id,
            Thread.is_active == True
        ).first()
    
    def update_thread(
        self,
        thread_id: uuid.UUID,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Thread]:
        """Update a thread."""
        thread = self.get_thread(thread_id)
        if not thread:
            return None
        
        if metadata is not None:
            thread.metadata = metadata
        
        self.db.commit()
        self.db.refresh(thread)
        
        return thread
    
    def delete_thread(self, thread_id: uuid.UUID) -> bool:
        """Soft delete a thread."""
        thread = self.get_thread(thread_id)
        if not thread:
            return False
        
        thread.is_active = False
        self.db.commit()
        
        return True
    
    def update_last_message_time(self, thread_id: uuid.UUID) -> None:
        """Update the last message timestamp for a thread."""
        thread = self.get_thread(thread_id)
        if thread:
            thread.last_message_at = datetime.utcnow()
            self.db.commit()