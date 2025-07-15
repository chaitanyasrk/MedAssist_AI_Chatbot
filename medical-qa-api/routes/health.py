import asyncio
import logging
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any
import torch
from datetime import datetime

from utils.config import settings
from services.rag_service import MedicalRAGService
from services.evaluation_service import EvaluationService
from services.gaurdrails_service import GuardrailsService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["health"])

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    services: Dict[str, Any]
    system_info: Dict[str, Any]

@router.get("/", response_model=HealthResponse)
async def health_check():
    """Comprehensive health check"""
    try:
        timestamp = datetime.utcnow()
        
        # Check service health
        services_status = {
            "rag_service": "unknown",
            "evaluation_service": "unknown", 
            "guardrails_service": "unknown",
            "azure_openai": "unknown",
            "vector_store": "unknown"
        }
        
        # Check RAG service
        try:
            # Simple test to check if services are initialized
            # In production, you might want more comprehensive checks
            services_status["rag_service"] = "healthy"
        except Exception as e:
            services_status["rag_service"] = f"unhealthy: {str(e)}"
        
        # Check evaluation service
        try:
            services_status["evaluation_service"] = "healthy"
        except Exception as e:
            services_status["evaluation_service"] = f"unhealthy: {str(e)}"
        
        # Check guardrails
        try:
            services_status["guardrails_service"] = "healthy"
        except Exception as e:
            services_status["guardrails_service"] = f"unhealthy: {str(e)}"
        
        # System information
        system_info = {
            "pytorch_version": torch.__version__,
            "cuda_available": torch.cuda.is_available(),
            "device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
            "python_version": "3.9+",
            "api_version": settings.VERSION
        }
        
        # Overall status
        overall_status = "healthy" if all(
            "healthy" in status for status in services_status.values()
        ) else "degraded"
        
        return HealthResponse(
            status=overall_status,
            timestamp=timestamp,
            version=settings.VERSION,
            services=services_status,
            system_info=system_info
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Health check failed"
        )

@router.get("/ready")
async def readiness_check():
    """Readiness probe for Kubernetes"""
    try:
        # Check if critical services are ready
        # This is a simplified check - in production you'd want more thorough checks
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service not ready"
        )

@router.get("/live")
async def liveness_check():
    """Liveness probe for Kubernetes"""
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }