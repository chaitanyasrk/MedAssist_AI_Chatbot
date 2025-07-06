"""
Pydantic models for chat functionality
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class DocumentType(str, Enum):
    """Document types"""
    TROUBLESHOOTING = "troubleshooting"
    API_DOCUMENTATION = "api_documentation"
    KNOWLEDGE_BASE = "knowledge_base"


class ChatRequest(BaseModel):
    """Chat request model"""
    query: str = Field(..., description="User query")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")
    bearer_token: Optional[str] = Field(None, description="Bearer token for API execution")
    include_context: bool = Field(default=True, description="Whether to include context from documents")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "How do I troubleshoot CPQ API authentication issues?",
                "conversation_id": "conv_123",
                "bearer_token": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "include_context": True
            }
        }


class ChatMessage(BaseModel):
    """Individual chat message"""
    role: str = Field(..., description="Message role (user/assistant)")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    context_used: bool = Field(default=False, description="Whether context was used")
    confidence_score: Optional[float] = Field(None, description="Response confidence score")


class APICallInfo(BaseModel):
    """API call information"""
    endpoint: str = Field(..., description="API endpoint")
    method: str = Field(..., description="HTTP method")
    headers: Optional[Dict[str, str]] = Field(None, description="Required headers")
    payload_schema: Optional[Dict[str, Any]] = Field(None, description="Expected payload schema")
    description: str = Field(..., description="API description")


class ChatResponse(BaseModel):
    """Chat response model"""
    response: str = Field(..., description="Generated response")
    context_used: bool = Field(..., description="Whether context from documents was used")
    confidence_score: float = Field(..., description="Response confidence score")
    requires_api_execution: bool = Field(default=False, description="Whether API execution is required")
    api_info: Optional[APICallInfo] = Field(None, description="API information if execution required")
    suggested_follow_ups: Optional[List[str]] = Field(None, description="Suggested follow-up questions")
    conversation_id: Optional[str] = Field(None, description="Conversation ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "To troubleshoot CPQ API authentication, check your bearer token validity...",
                "context_used": True,
                "confidence_score": 0.85,
                "requires_api_execution": False,
                "suggested_follow_ups": [
                    "How do I refresh my bearer token?",
                    "What are common authentication error codes?"
                ]
            }
        }


class DocumentUploadRequest(BaseModel):
    """Document upload request"""
    content: str = Field(..., description="Document content")
    filename: str = Field(..., description="Document filename")
    document_type: DocumentType = Field(..., description="Type of document")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": "# CPQ Troubleshooting Guide\n\n## Authentication Issues...",
                "filename": "cpq_troubleshooting.md",
                "document_type": "troubleshooting",
                "metadata": {"version": "1.0", "author": "Technical Team"}
            }
        }


class ConversationSummary(BaseModel):
    """Conversation summary"""
    conversation_id: str
    created_at: datetime
    last_updated: datetime
    message_count: int
    title: Optional[str] = None
    summary: Optional[str] = None


class Conversation(BaseModel):
    """Full conversation model"""
    conversation_id: str
    messages: List[ChatMessage]
    created_at: datetime
    last_updated: datetime
    metadata: Optional[Dict[str, Any]] = None