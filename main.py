"""
Troubleshooting Chatbot API
Main FastAPI application with Azure OpenAI integration
"""

from datetime import datetime
import os
import logging
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import asyncio
from contextlib import asynccontextmanager

from services.document_service import DocumentService
from services.chat_service import ChatService
from services.api_executor import APIExecutor
from services.evaluation_service import EvaluationService
from services.gaurdrails_service import GuardrailsService
from models.chat_models import ChatRequest, ChatResponse, DocumentUploadRequest
from models.evalution_models import EvaluationMetrics, EvaluationRequest
from config.settings import Settings
import importlib
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize settings
settings = Settings()

# Security
security = HTTPBearer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("Starting up Troubleshooting Chatbot API...")
    
    # Initialize services
    app.state.document_service = DocumentService()
    app.state.chat_service = ChatService()
    app.state.api_executor = APIExecutor()
    app.state.evaluation_service = EvaluationService()
    app.state.guardrails_service = GuardrailsService()
    
    # Load initial documents
    await app.state.document_service.load_default_documents()
    
    yield
    
    logger.info("Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Troubleshooting Chatbot API",
    description="AI-powered troubleshooting assistant with RAG capabilities",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}


# Document management endpoints
@app.post("/api/documents/upload")
async def upload_document(request: DocumentUploadRequest):
    """Upload and process troubleshooting document"""
    try:
        document_service: DocumentService = app.state.document_service
        result = await document_service.process_document(
            content=request.content,
            filename=request.filename,
            document_type=request.document_type
        )
        return {"message": "Document processed successfully", "document_id": result}
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/documents")
async def list_documents():
    """List all processed documents"""
    try:
        document_service: DocumentService = app.state.document_service
        documents = await document_service.list_documents()
        return {"documents": documents}
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Chat endpoints
@app.post("/api/chat", response_model=ChatResponse)
async def chat_query(request: ChatRequest):
    """Process chat query with RAG"""
    try:
        # Apply guardrails
        guardrails_service: GuardrailsService = app.state.guardrails_service
        is_safe = await guardrails_service.validate_input(request.query)
        
        if not is_safe:
            return ChatResponse(
                response="Sorry! Your query contains inappropriate content. Please rephrase your question.",
                context_used=False,
                confidence_score=0.0,
                requires_api_execution=False
            )
        
        # Process chat query
        chat_service: ChatService = app.state.chat_service
        response = await chat_service.process_query(
            query=request.query,
            conversation_id=request.conversation_id,
            bearer_token=request.bearer_token
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing chat query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat/execute-api")
async def execute_api(
    api_endpoint: str,
    bearer_token: str,
    payload: Optional[Dict[Any, Any]] = None
):
    """Execute API call with provided bearer token"""
    try:
        api_executor: APIExecutor = app.state.api_executor
        result = await api_executor.execute_api_call(
            endpoint=api_endpoint,
            bearer_token=bearer_token,
            payload=payload
        )
        return result
    except Exception as e:
        logger.error(f"Error executing API: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Evaluation endpoints
@app.post("/api/evaluation/evaluate", response_model=EvaluationMetrics)
async def evaluate_response(request: EvaluationRequest):
    """Evaluate response quality against golden dataset"""
    try:
        evaluation_service: EvaluationService = app.state.evaluation_service
        metrics = await evaluation_service.evaluate_response(
            query=request.query,
            generated_response=request.generated_response,
            expected_response=request.expected_response
        )
        return metrics
    except Exception as e:
        logger.error(f"Error evaluating response: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/evaluation/metrics", response_model=Dict[str, Any])
async def get_evaluation_metrics():
    """Get overall evaluation metrics"""
    try:
        evaluation_service: EvaluationService = app.state.evaluation_service
        metrics = await evaluation_service.get_overall_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Error getting evaluation metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/evaluation/golden-dataset")
async def get_golden_dataset():
    """Get golden dataset for evaluation"""
    try:
        evaluation_service: EvaluationService = app.state.evaluation_service
        dataset = await evaluation_service.get_golden_dataset()
        return {"dataset": dataset}
    except Exception as e:
        logger.error(f"Error getting golden dataset: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Conversation management
@app.get("/api/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get conversation history"""
    try:
        chat_service: ChatService = app.state.chat_service
        conversation = await chat_service.get_conversation(conversation_id)
        return {"conversation": conversation}
    except Exception as e:
        logger.error(f"Error getting conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete conversation history"""
    try:
        chat_service: ChatService = app.state.chat_service
        await chat_service.delete_conversation(conversation_id)
        return {"message": "Conversation deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/api/admin/reload-config")
async def reload_config():
    """Reload configuration and environment variables"""
    try:
        # Force reload environment variables
        load_dotenv(override=True)
        
        # Reload settings module
        import config.settings
        importlib.reload(config.settings)
        
        # Reload services
        import services.chat_service
        import services.document_service
        importlib.reload(services.chat_service)
        importlib.reload(services.document_service)
        
        # Re-initialize services with new settings
        app.state.chat_service = ChatService()
        app.state.document_service = DocumentService()
        
        return {
            "message": "Configuration reloaded successfully",
            "timestamp": datetime.utcnow().isoformat(),
            "api_version": os.getenv("AZURE_OPENAI_API_VERSION")
        }
    except Exception as e:
        logger.error(f"Error reloading configuration: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/admin/config-status")
async def get_config_status():
    """Get current configuration status"""
    return {
        "azure_openai_api_version": os.getenv("AZURE_OPENAI_API_VERSION"),
        "azure_openai_endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
        "azure_openai_deployment_name": os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        "env_file_exists": os.path.exists(".env"),
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )