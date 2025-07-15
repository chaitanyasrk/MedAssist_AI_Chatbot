from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, nullable=False)
    message_type = Column(String, nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=func.now())
    
    # Metadata
    evaluation_score = Column(Float, nullable=True)
    retrieved_context = Column(JSON, nullable=True)
    response_time = Column(Float, nullable=True)

class EvaluationResult(Base):
    __tablename__ = "evaluation_results"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(Integer, nullable=False)
    
    # Evaluation metrics
    relevance_score = Column(Float, nullable=False)
    accuracy_score = Column(Float, nullable=False)
    completeness_score = Column(Float, nullable=False)
    safety_score = Column(Float, nullable=False)
    
    overall_score = Column(Float, nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    # Additional metadata
    evaluation_method = Column(String, nullable=False)
    reference_answer = Column(Text, nullable=True)