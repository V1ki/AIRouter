from sqlalchemy import Column, DateTime, String, ForeignKey, Enum, Integer, Float, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
import enum
from datetime import datetime

from app.db.database import Base


class RunStatus(str, enum.Enum):
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    REQUIRES_ACTION = "requires_action"
    CANCELLING = "cancelling"
    CANCELLED = "cancelled"
    FAILED = "failed"
    COMPLETED = "completed"
    EXPIRED = "expired"
    
    def __str__(self):
        return self.value


class Run(Base):
    """
    Represents an execution run of an assistant on a thread.
    Compatible with OpenAI Runs API v1 structure.
    """
    __tablename__ = "runs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    object = Column(String, default="thread.run")  # Always "thread.run" for API compatibility
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    thread_id = Column(UUID(as_uuid=True), ForeignKey("threads.id"), nullable=False)
    assistant_id = Column(UUID(as_uuid=True), ForeignKey("assistants.id"), nullable=False)
    status = Column(Enum(RunStatus), nullable=False, default=RunStatus.QUEUED)
    required_action = Column(JSONB, nullable=True)  # Details about required action
    last_error = Column(JSONB, nullable=True)  # Details about the last error
    expires_at = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    failed_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    model = Column(String, nullable=False)  # The model used for this run
    instructions = Column(Text, nullable=True)  # Instructions override for this run
    tools = Column(JSONB, nullable=False, default=list)  # List of tools for this run
    file_ids = Column(JSONB, nullable=False, default=list)  # List of file IDs
    meta_data = Column(JSONB, nullable=True)  # Custom metadata
    
    # Usage tracking
    usage = Column(JSONB, nullable=True)  # Token usage information
    temperature = Column(Float, nullable=True)
    max_prompt_tokens = Column(Integer, nullable=True)
    max_completion_tokens = Column(Integer, nullable=True)
    
    # Additional fields
    provider_id = Column(UUID(as_uuid=True), ForeignKey("model_providers.id"), nullable=True)
    
    # Relationships
    thread = relationship("Thread", back_populates="runs")
    assistant = relationship("Assistant", backref="runs")
    provider = relationship("ModelProvider", backref="runs")
    steps = relationship("RunStep", back_populates="run", cascade="all, delete-orphan", order_by="RunStep.created_at")
    messages = relationship("Message", back_populates="run")
    
    def to_dict(self):
        """Convert run to API response format"""
        return {
            "id": f"run_{str(self.id).replace('-', '')}",  # Format as OpenAI style ID
            "object": self.object,
            "created_at": int(self.created_at.timestamp()),
            "thread_id": f"thread_{str(self.thread_id).replace('-', '')}",
            "assistant_id": f"asst_{str(self.assistant_id).replace('-', '')}",
            "status": self.status.value,
            "required_action": self.required_action,
            "last_error": self.last_error,
            "expires_at": int(self.expires_at.timestamp()) if self.expires_at else None,
            "started_at": int(self.started_at.timestamp()) if self.started_at else None,
            "cancelled_at": int(self.cancelled_at.timestamp()) if self.cancelled_at else None,
            "failed_at": int(self.failed_at.timestamp()) if self.failed_at else None,
            "completed_at": int(self.completed_at.timestamp()) if self.completed_at else None,
            "model": self.model,
            "instructions": self.instructions,
            "tools": self.tools or [],
            "file_ids": self.file_ids or [],
            "metadata": self.meta_data or {},
            "usage": self.usage
        }