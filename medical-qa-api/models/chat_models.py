from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class MessageType(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class ChatMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="User message")
    session_id: Optional[str] = Field(None, description="Chat session ID")

class ChatMessageResponse(BaseModel):
    message_id: int
    session_id: str
    response: str
    evaluation_score: Optional[float] = None
    retrieved_context: List[Dict[str, Any]] = []
    response_time: float
    timestamp: datetime
    is_medical: bool
    query_type: Optional[str] = None

class ChatHistoryRequest(BaseModel):
    session_id: str
    limit: Optional[int] = Field(50, ge=1, le=100)
    offset: Optional[int] = Field(0, ge=0)

class ChatHistoryResponse(BaseModel):
    session_id: str
    messages: List[Dict[str, Any]]
    total_count: int
    has_more: bool

class ChatSessionResponse(BaseModel):
    session_id: str
    created_at: datetime
    message_count: int
    is_active: bool