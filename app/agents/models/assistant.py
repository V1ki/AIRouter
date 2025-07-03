from sqlalchemy import Column, DateTime, String, ForeignKey, Enum, Boolean, Integer, ARRAY, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
import enum
from datetime import datetime

from app.db.database import Base


class Assistant(Base):
    """
    Represents an AI assistant that can be used to interact with users.
    Compatible with OpenAI Assistants API v1 structure.
    """
    __tablename__ = "assistants"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    object = Column(String, default="assistant")  # Always "assistant" for API compatibility
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    name = Column(String(256), nullable=True)
    description = Column(String(512), nullable=True)
    model = Column(String, nullable=False)  # The model ID to use
    instructions = Column(Text, nullable=True)  # System instructions for the assistant
    tools = Column(JSONB, nullable=False, default=list)  # List of tools enabled (code_interpreter, retrieval, function)
    file_ids = Column(ARRAY(String), nullable=False, default=list)  # List of file IDs attached
    meta_data = Column(JSONB, nullable=True)  # Custom metadata
    
    # Additional fields for routing and management
    provider_id = Column(UUID(as_uuid=True), ForeignKey("model_providers.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    provider = relationship("ModelProvider", backref="assistants")
    threads = relationship("Thread", secondary="thread_assistants", back_populates="assistants")
    
    def to_dict(self):
        """Convert assistant to API response format"""
        return {
            "id": f"asst_{str(self.id).replace('-', '')}",  # Format as OpenAI style ID
            "object": self.object,
            "created_at": int(self.created_at.timestamp()),
            "name": self.name,
            "description": self.description,
            "model": self.model,
            "instructions": self.instructions,
            "tools": self.tools or [],
            "file_ids": self.file_ids or [],
            "metadata": self.meta_data or {}
        }