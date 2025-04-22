from sqlalchemy import Column, Float, String, ForeignKey, Boolean, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

from app.db.database import Base

class Response(Base):
    """ """
    __tablename__ = "responses"
    
    id = Column(String, primary_key=True)
    #created_at number
    # Unix timestamp (in seconds) of when this Response was created.
    created_at = Column(Integer, nullable=False)
    
    # error code and message
    error = Column(JSONB, nullable=True)
    
    # incomplete_details jsonb 
    # Details about the response that was incomplete.
    incomplete_details = Column(JSONB, nullable=True)
    
    # instructions string
    # The instructions that were used to generate the response.
    instructions = Column(String, nullable=True)
    
    # max_output_tokens integer
    # The maximum number of tokens that were allowed in the response.
    max_output_tokens = Column(Integer, nullable=True)
    
    # metadata jsonb
    # Set of 16 key-value pairs that can be attached to an object. This can be useful for storing additional information about the object in a structured format, and querying for objects via API or the dashboard.
    # Keys are strings with a maximum length of 64 characters. Values are strings with a maximum length of 512 characters.
    meta_data = Column(JSONB, nullable=True)
    
    # model string
    # The model that was used to generate the response.
    model = Column(String, nullable=True)   
    
    # output jsonb
    # The output of the response.
    output = Column(JSONB, nullable=True)
    
    # parallel_tool_calls boolean
    # Whether the response was generated in parallel.
    parallel_tool_calls = Column(Boolean, nullable=True)
    
    # previous_response_id string
    # The ID of the previous response.
    previous_response_id = Column(String, nullable=True)
    
    # reasoning jsonb
    # The reasoning behind the response.
    reasoning = Column(JSONB, nullable=True)
    
    # status string
    # The status of the response generation. One of completed, failed, in_progress, or incomplete.
    status = Column(String, nullable=True)
    
    # temperature float
    # The temperature of the response.
    temperature = Column(Float, nullable=True)
    
    # text jsonb
    # The text of the response.
    text = Column(JSONB, nullable=True)
    
    # tool_choice string
    # The tool choice of the response.
    tool_choice = Column(String, nullable=True)
    
    # tools jsonb
    # The tools of the response.
    tools = Column(JSONB, nullable=True)
    
    # top_p float
    # The top P of the response.
    top_p = Column(Float, nullable=True)
    
    # truncation string
    # The truncation of the response.
    truncation = Column(String, nullable=True)
    
    # usage jsonb
    # The usage of the response.
    usage = Column(JSONB, nullable=True)
    
    # user string
    # The user of the response.
    user = Column(String, nullable=True)
    
    # message_items 
    # The message items of the response.
    message_items = relationship("MessageItem", back_populates="response", cascade="all, delete-orphan")
    
class MessageItem(Base):
    """ """
    __tablename__ = "message_items"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    role = Column(String, nullable=False)
    content = Column(JSONB, nullable=False)
    
    # response_id string
    # The ID of the response.
    response_id = Column(String, ForeignKey("responses.id"), nullable=False)
    
    response = relationship("Response", back_populates="message_items")  
    