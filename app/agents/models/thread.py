from sqlalchemy import Column, DateTime, String, ForeignKey, Boolean, Table
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from datetime import datetime

from app.db.database import Base


# Association table for many-to-many relationship between threads and assistants
thread_assistants = Table(
    'thread_assistants',
    Base.metadata,
    Column('thread_id', UUID(as_uuid=True), ForeignKey('threads.id'), primary_key=True),
    Column('assistant_id', UUID(as_uuid=True), ForeignKey('assistants.id'), primary_key=True),
    Column('created_at', DateTime(timezone=True), default=datetime.utcnow)
)


class Thread(Base):
    """
    Represents a conversation thread that can contain multiple messages.
    Compatible with OpenAI Threads API v1 structure.
    """
    __tablename__ = "threads"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    object = Column(String, default="thread")  # Always "thread" for API compatibility
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    meta_data = Column(JSONB, nullable=True)  # Custom metadata
    
    # Additional fields for management
    is_active = Column(Boolean, default=True)
    last_message_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    messages = relationship("Message", back_populates="thread", cascade="all, delete-orphan", order_by="Message.created_at")
    runs = relationship("Run", back_populates="thread", cascade="all, delete-orphan")
    assistants = relationship("Assistant", secondary=thread_assistants, back_populates="threads")
    
    def to_dict(self):
        """Convert thread to API response format"""
        return {
            "id": f"thread_{str(self.id).replace('-', '')}",  # Format as OpenAI style ID
            "object": self.object,
            "created_at": int(self.created_at.timestamp()),
            "metadata": self.meta_data or {}
        }