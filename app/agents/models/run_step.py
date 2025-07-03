from sqlalchemy import Column, DateTime, String, ForeignKey, Enum, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
import enum
from datetime import datetime

from app.db.database import Base


class RunStepType(str, enum.Enum):
    MESSAGE_CREATION = "message_creation"
    TOOL_CALLS = "tool_calls"
    
    def __str__(self):
        return self.value


class RunStepStatus(str, enum.Enum):
    IN_PROGRESS = "in_progress"
    CANCELLED = "cancelled"
    FAILED = "failed"
    COMPLETED = "completed"
    EXPIRED = "expired"
    
    def __str__(self):
        return self.value


class RunStep(Base):
    """
    Represents a step in the execution of a run.
    Compatible with OpenAI Run Steps API v1 structure.
    """
    __tablename__ = "run_steps"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    object = Column(String, default="thread.run.step")  # Always "thread.run.step" for API compatibility
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    run_id = Column(UUID(as_uuid=True), ForeignKey("runs.id"), nullable=False)
    assistant_id = Column(UUID(as_uuid=True), ForeignKey("assistants.id"), nullable=False)
    thread_id = Column(UUID(as_uuid=True), ForeignKey("threads.id"), nullable=False)
    type = Column(Enum(RunStepType), nullable=False)
    status = Column(Enum(RunStepStatus), nullable=False, default=RunStepStatus.IN_PROGRESS)
    step_details = Column(JSONB, nullable=False)  # Details specific to the step type
    last_error = Column(JSONB, nullable=True)  # Details about the last error
    expired_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    failed_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    meta_data = Column(JSONB, nullable=True)  # Custom metadata
    usage = Column(JSONB, nullable=True)  # Token usage for this step
    
    # Relationships
    run = relationship("Run", back_populates="steps")
    assistant = relationship("Assistant", backref="run_steps")
    thread = relationship("Thread", backref="run_steps")
    
    def to_dict(self):
        """Convert run step to API response format"""
        return {
            "id": f"step_{str(self.id).replace('-', '')}",  # Format as OpenAI style ID
            "object": self.object,
            "created_at": int(self.created_at.timestamp()),
            "run_id": f"run_{str(self.run_id).replace('-', '')}",
            "assistant_id": f"asst_{str(self.assistant_id).replace('-', '')}",
            "thread_id": f"thread_{str(self.thread_id).replace('-', '')}",
            "type": self.type.value,
            "status": self.status.value,
            "step_details": self.step_details,
            "last_error": self.last_error,
            "expired_at": int(self.expired_at.timestamp()) if self.expired_at else None,
            "cancelled_at": int(self.cancelled_at.timestamp()) if self.cancelled_at else None,
            "failed_at": int(self.failed_at.timestamp()) if self.failed_at else None,
            "completed_at": int(self.completed_at.timestamp()) if self.completed_at else None,
            "metadata": self.meta_data or {},
            "usage": self.usage
        }