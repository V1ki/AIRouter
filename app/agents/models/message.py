from sqlalchemy import Column, DateTime, String, ForeignKey, Enum, Integer, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
import enum
from datetime import datetime

from app.db.database import Base


class MessageRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    
    def __str__(self):
        return self.value


class MessageStatus(str, enum.Enum):
    IN_PROGRESS = "in_progress"
    INCOMPLETE = "incomplete"
    COMPLETED = "completed"
    
    def __str__(self):
        return self.value


class Message(Base):
    """
    Represents a message within a thread.
    Compatible with OpenAI Messages API v1 structure.
    """
    __tablename__ = "messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    object = Column(String, default="thread.message")  # Always "thread.message" for API compatibility
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    thread_id = Column(UUID(as_uuid=True), ForeignKey("threads.id"), nullable=False)
    role = Column(Enum(MessageRole), nullable=False)
    content = Column(JSONB, nullable=False)  # Array of content objects (text, image_file)
    assistant_id = Column(UUID(as_uuid=True), ForeignKey("assistants.id"), nullable=True)
    run_id = Column(UUID(as_uuid=True), ForeignKey("runs.id"), nullable=True)
    file_ids = Column(JSONB, nullable=False, default=list)  # List of file IDs
    meta_data = Column(JSONB, nullable=True)  # Custom metadata
    
    # Additional fields
    status = Column(Enum(MessageStatus), default=MessageStatus.COMPLETED)
    incomplete_details = Column(JSONB, nullable=True)  # Details about why message is incomplete
    completed_at = Column(DateTime(timezone=True), nullable=True)
    incomplete_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    thread = relationship("Thread", back_populates="messages")
    assistant = relationship("Assistant", backref="messages")
    run = relationship("Run", back_populates="messages")
    
    def to_dict(self):
        """Convert message to API response format"""
        return {
            "id": f"msg_{str(self.id).replace('-', '')}",  # Format as OpenAI style ID
            "object": self.object,
            "created_at": int(self.created_at.timestamp()),
            "thread_id": f"thread_{str(self.thread_id).replace('-', '')}",
            "role": self.role.value,
            "content": self.content or [],
            "assistant_id": f"asst_{str(self.assistant_id).replace('-', '')}" if self.assistant_id else None,
            "run_id": f"run_{str(self.run_id).replace('-', '')}" if self.run_id else None,
            "file_ids": self.file_ids or [],
            "metadata": self.meta_data or {}
        }