"""
Complete chat route with RAG and Azure OpenAI integration
"""

import asyncio
import logging
import time
import uuid
from typing import List, Dict, Any
from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select, func, desc

from database.connection import get_db
from database.models import ChatSession, ChatMessage
from models.chat_models import (
    ChatMessageRequest, ChatMessageResponse, 
    ChatHistoryRequest, ChatHistoryResponse,
    ChatSessionResponse, MessageType
)
from services.rag_service import MedicalRAGService
from services.evaluation_service import EvaluationService
from services.gaurdrails_service import GuardrailsService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

# Global service instances - Initialize once
rag_service = None
evaluation_service = None
guardrails_service = None

async def initialize_services():
    """Initialize all services once"""
    global rag_service, evaluation_service, guardrails_service
    
    if rag_service is None:
        try:
            logger.info("Initializing chat services...")
            
            # Initialize services
            rag_service = MedicalRAGService()
            evaluation_service = EvaluationService()
            guardrails_service = GuardrailsService()
            
            # Initialize each service
            await rag_service.initialize()
            await evaluation_service.initialize()
            await guardrails_service.initialize()
            
            logger.info("✅ All chat services initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Error initializing chat services: {e}")
            # Fall back to basic functionality if services fail
            rag_service = None
            evaluation_service = None
            guardrails_service = None
            raise

@router.post("/message", response_model=ChatMessageResponse)
async def send_message(request: ChatMessageRequest):
    """Send a message and get AI response with RAG"""
    start_time = time.time()
    
    try:
        # Initialize services if not already done
        await initialize_services()
        
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Enhanced processing with RAG and Azure OpenAI
        if rag_service and evaluation_service and guardrails_service:
            response_data = await _process_with_rag(request, session_id, start_time)
        else:
            # Fallback to basic processing if services failed to initialize
            logger.warning("Using fallback processing - RAG services not available")
            response_data = await _process_basic(request, session_id, start_time)
        
        return response_data
        
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        
        # Try fallback processing
        try:
            logger.info("Attempting fallback processing...")
            response_data = await _process_basic(request, session_id or str(uuid.uuid4()), start_time)
            return response_data
        except Exception as fallback_error:
            logger.error(f"Fallback processing also failed: {str(fallback_error)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to process message: {str(e)}"
            )

async def _process_with_rag(request: ChatMessageRequest, session_id: str, start_time: float) -> ChatMessageResponse:
    """Process message with full RAG and Azure OpenAI"""
    try:
        # Step 1: Check input with guardrails
        is_safe_input, rejection_message = await guardrails_service.check_input(request.message)
        if not is_safe_input:
            # Save rejected message
            async with get_db() as db:
                await _save_message_to_db(db, session_id, request.message, MessageType.USER)
                assistant_msg = await _save_message_to_db(db, session_id, rejection_message, MessageType.ASSISTANT)
            
            response_time = time.time() - start_time
            return ChatMessageResponse(
                message_id=assistant_msg.id,
                session_id=session_id,
                response=rejection_message,
                response_time=response_time,
                timestamp=assistant_msg.timestamp,
                is_medical=False
            )
        
        # Step 2: Process query with RAG
        logger.info(f"Processing query with RAG: {request.message[:100]}...")
        rag_result = await rag_service.process_query(request.message, session_id)
        
        # Step 3: Check output with guardrails
        if rag_result["evaluation_ready"]:
            is_safe_output, safety_message = await guardrails_service.check_output(rag_result["response"])
            if not is_safe_output:
                rag_result["response"] = safety_message
                rag_result["evaluation_ready"] = False
        
        # Step 4: Add medical disclaimer
        if rag_result["is_medical"]:
            rag_result["response"] += guardrails_service.get_medical_disclaimer()
        
        # Step 5: Evaluate response quality
        evaluation_score = None
        if rag_result["evaluation_ready"] and rag_result.get("retrieved_context"):
            try:
                # Use first retrieved context as reference for evaluation
                reference_answer = rag_result["retrieved_context"][0].get("answer", "")
                eval_result = await evaluation_service.evaluate_response(
                    request.message,
                    rag_result["response"],
                    reference_answer,
                    rag_result["retrieved_context"]
                )
                evaluation_score = eval_result["overall_score"]
                logger.info(f"Response evaluation score: {evaluation_score:.2f}")
            except Exception as e:
                logger.warning(f"Evaluation failed: {e}")
                evaluation_score = 0.5  # Default score if evaluation fails
        
        # Step 6: Save to database
        async with get_db() as db:
            # Save user message
            await _save_message_to_db(db, session_id, request.message, MessageType.USER)
            
            # Save assistant response
            assistant_message = await _save_message_to_db(
                db, session_id, rag_result["response"], MessageType.ASSISTANT,
                evaluation_score=evaluation_score,
                retrieved_context=rag_result.get("retrieved_context", [])
            )
        
        response_time = time.time() - start_time
        logger.info(f"RAG processing completed in {response_time:.2f}s")
        
        return ChatMessageResponse(
            message_id=assistant_message.id,
            session_id=session_id,
            response=rag_result["response"],
            evaluation_score=evaluation_score,
            retrieved_context=rag_result.get("retrieved_context", []),
            response_time=response_time,
            timestamp=assistant_message.timestamp,
            is_medical=rag_result["is_medical"],
            query_type=rag_result.get("query_type")
        )
        
    except Exception as e:
        logger.error(f"Error in RAG processing: {str(e)}")
        raise

async def _process_basic(request: ChatMessageRequest, session_id: str, start_time: float) -> ChatMessageResponse:
    """Fallback basic processing without RAG"""
    logger.info("Using basic processing (no RAG)")
    
    # Simple medical validation
    medical_keywords = [
        "diabetes", "hypertension", "symptoms", "disease", "medical", "health", 
        "doctor", "treatment", "medication", "diagnosis", "therapy", "condition",
        "syndrome", "infection", "virus", "bacteria", "pain", "fever", "heart",
        "blood", "pressure", "cholesterol", "cancer", "tumor", "surgery"
    ]
    is_medical = any(keyword.lower() in request.message.lower() for keyword in medical_keywords)
    
    if not is_medical:
        response_text = "I'm sorry, but I can only answer medical and healthcare-related questions. Please ask about medical conditions, treatments, medications, anatomy, or physiology."
        evaluation_score = 0.0
    else:
        # Enhanced basic medical response
        response_text = f"""Based on your question about "{request.message}", I can provide some general medical information.

However, this is currently running in basic mode without access to the full medical knowledge base. For complete answers with citations and detailed explanations, the RAG system with Azure OpenAI needs to be properly configured.

**Medical Disclaimer**: This information is for educational purposes only and should not be considered as medical advice. Always consult with qualified healthcare professionals for personal medical concerns, diagnosis, or treatment decisions."""
        evaluation_score = 0.6
    
    # Save to database
    async with get_db() as db:
        # Save user message
        await _save_message_to_db(db, session_id, request.message, MessageType.USER)
        
        # Save assistant response
        assistant_message = await _save_message_to_db(
            db, session_id, response_text, MessageType.ASSISTANT,
            evaluation_score=evaluation_score,
            retrieved_context=[]
        )
    
    response_time = time.time() - start_time
    
    return ChatMessageResponse(
        message_id=assistant_message.id,
        session_id=session_id,
        response=response_text,
        evaluation_score=evaluation_score,
        retrieved_context=[],
        response_time=response_time,
        timestamp=assistant_message.timestamp,
        is_medical=is_medical,
        query_type="general" if is_medical else "non-medical"
    )

async def _save_message_to_db(
    db,
    session_id: str,
    content: str,
    message_type: MessageType,
    evaluation_score: float = None,
    retrieved_context: List[Dict] = None
) -> ChatMessage:
    """Save message to database"""
    # Create session if doesn't exist
    session_query = select(ChatSession).where(ChatSession.id == session_id)
    existing_session = await db.scalar(session_query)
    
    if not existing_session:
        new_session = ChatSession(
            id=session_id,
            user_id="default_user",
            is_active=True
        )
        db.add(new_session)
        await db.flush()
    
    # Create message
    message = ChatMessage(
        session_id=session_id,
        message_type=message_type.value,
        content=content,
        evaluation_score=evaluation_score,
        retrieved_context=retrieved_context or []
    )
    
    db.add(message)
    await db.commit()
    await db.refresh(message)
    
    return message

# Keep the existing history and session endpoints
@router.get("/history/{session_id}", response_model=ChatHistoryResponse)
async def get_chat_history(
    session_id: str,
    limit: int = 50,
    offset: int = 0
):
    """Get chat history for a session"""
    try:
        async with get_db() as db:
            # Get total count
            count_query = select(func.count(ChatMessage.id)).where(
                ChatMessage.session_id == session_id
            )
            total_count = await db.scalar(count_query) or 0
            
            # Get messages
            query = select(ChatMessage).where(
                ChatMessage.session_id == session_id
            ).order_by(ChatMessage.timestamp).limit(limit).offset(offset)
            
            result = await db.execute(query)
            messages = result.scalars().all()
            
            # Convert to response format
            message_list = []
            for msg in messages:
                message_list.append({
                    "id": msg.id,
                    "message_type": msg.message_type,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "evaluation_score": msg.evaluation_score,
                    "retrieved_context": msg.retrieved_context or []
                })
            
            has_more = offset + limit < total_count
            
            return ChatHistoryResponse(
                session_id=session_id,
                messages=message_list,
                total_count=total_count,
                has_more=has_more
            )
        
    except Exception as e:
        logger.error(f"Error getting chat history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve chat history: {str(e)}"
        )

@router.get("/sessions", response_model=List[ChatSessionResponse])
async def get_chat_sessions(limit: int = 20, offset: int = 0):
    """Get chat sessions"""
    try:
        async with get_db() as db:
            query = select(ChatSession).order_by(
                desc(ChatSession.created_at)
            ).limit(limit).offset(offset)
            
            result = await db.execute(query)
            sessions = result.scalars().all()
            
            session_list = []
            for session in sessions:
                count_query = select(func.count(ChatMessage.id)).where(
                    ChatMessage.session_id == session.id
                )
                message_count = await db.scalar(count_query) or 0
                
                session_list.append(ChatSessionResponse(
                    session_id=session.id,
                    created_at=session.created_at,
                    message_count=message_count,
                    is_active=session.is_active
                ))
            
            return session_list
        
    except Exception as e:
        logger.error(f"Error getting chat sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve chat sessions: {str(e)}"
        )

@router.delete("/session/{session_id}")
async def delete_chat_session(session_id: str):
    """Delete a chat session and its messages"""
    try:
        async with get_db() as db:
            await db.execute(
                ChatMessage.__table__.delete().where(ChatMessage.session_id == session_id)
            )
            await db.execute(
                ChatSession.__table__.delete().where(ChatSession.id == session_id)
            )
            await db.commit()
            
            return {"message": "Session deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting chat session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete chat session: {str(e)}"
        )