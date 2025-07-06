"""
Pydantic models for evaluation functionality
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class DifficultyLevel(str, Enum):
    """Difficulty levels for evaluation examples"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class EvaluationCategory(str, Enum):
    """Categories for evaluation examples"""
    AUTHENTICATION = "authentication"
    API_USAGE = "api_usage"
    TROUBLESHOOTING = "troubleshooting"
    CONFIGURATION = "configuration"
    ERROR_HANDLING = "error_handling"


class GoldenExample(BaseModel):
    """Golden example for evaluation"""
    query: str = Field(..., description="User query")
    expected_response: str = Field(..., description="Expected response")
    category: str = Field(..., description="Category of the example")
    difficulty: str = Field(..., description="Difficulty level")
    context_keywords: List[str] = Field(..., description="Keywords that should trigger this example")
    metadata: Optional[dict] = Field(None, description="Additional metadata")
    
    class Config:
        schema_extra = {
            "example": {
                "query": "How do I fix 401 authentication errors?",
                "expected_response": "For 401 authentication errors, check these steps...",
                "category": "authentication",
                "difficulty": "easy",
                "context_keywords": ["401", "authentication", "bearer token"],
                "metadata": {"created_by": "system", "version": "1.0"}
            }
        }


class EvaluationRequest(BaseModel):
    """Request for response evaluation"""
    query: str = Field(..., description="Original user query")
    generated_response: str = Field(..., description="Generated response to evaluate")
    expected_response: Optional[str] = Field(None, description="Expected response (if available)")
    evaluation_type: str = Field(default="comprehensive", description="Type of evaluation")
    
    class Config:
        schema_extra = {
            "example": {
                "query": "How do I troubleshoot API timeout errors?",
                "generated_response": "To fix timeout errors, increase the timeout value...",
                "expected_response": "For timeout errors, check network connectivity and increase timeout settings...",
                "evaluation_type": "comprehensive"
            }
        }


class EvaluationMetrics(BaseModel):
    """Evaluation metrics for a response"""
    correctness_score: float = Field(..., ge=0.0, le=1.0, description="Correctness score (0-1)")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Relevance score (0-1)")
    completeness_score: float = Field(..., ge=0.0, le=1.0, description="Completeness score (0-1)")
    overall_score: float = Field(..., ge=0.0, le=1.0, description="Overall score (0-1)")
    evaluation_timestamp: datetime = Field(..., description="When the evaluation was performed")
    feedback: Optional[str] = Field(None, description="Additional feedback")
    
    class Config:
        schema_extra = {
            "example": {
                "correctness_score": 0.85,
                "relevance_score": 0.90,
                "completeness_score": 0.80,
                "overall_score": 0.85,
                "evaluation_timestamp": "2024-01-15T10:30:00Z",
                "feedback": "Good response but could include more specific examples"
            }
        }


class BatchEvaluationRequest(BaseModel):
    """Request for batch evaluation of multiple responses"""
    evaluations: List[EvaluationRequest] = Field(..., description="List of evaluation requests")
    evaluation_id: Optional[str] = Field(None, description="Batch evaluation ID")
    
    class Config:
        schema_extra = {
            "example": {
                "evaluations": [
                    {
                        "query": "How to fix 401 errors?",
                        "generated_response": "Check your token...",
                        "expected_response": "Verify bearer token..."
                    }
                ],
                "evaluation_id": "batch_eval_123"
            }
        }


class BatchEvaluationResponse(BaseModel):
    """Response for batch evaluation"""
    evaluation_id: str = Field(..., description="Batch evaluation ID")
    total_evaluations: int = Field(..., description="Total number of evaluations")
    completed_evaluations: int = Field(..., description="Number of completed evaluations")
    average_metrics: EvaluationMetrics = Field(..., description="Average metrics across all evaluations")
    individual_results: List[EvaluationMetrics] = Field(..., description="Individual evaluation results")
    started_at: datetime = Field(..., description="When batch evaluation started")
    completed_at: Optional[datetime] = Field(None, description="When batch evaluation completed")
    
    class Config:
        schema_extra = {
            "example": {
                "evaluation_id": "batch_eval_123",
                "total_evaluations": 10,
                "completed_evaluations": 10,
                "average_metrics": {
                    "correctness_score": 0.85,
                    "relevance_score": 0.90,
                    "completeness_score": 0.80,
                    "overall_score": 0.85
                },
                "started_at": "2024-01-15T10:00:00Z",
                "completed_at": "2024-01-15T10:05:00Z"
            }
        }


class MetricsTrend(BaseModel):
    """Metrics trend over time"""
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    average_score: float = Field(..., description="Average score for the day")
    evaluation_count: int = Field(..., description="Number of evaluations")
    category_breakdown: dict = Field(..., description="Breakdown by category")


class EvaluationSummary(BaseModel):
    """Summary of evaluation metrics"""
    total_evaluations: int = Field(..., description="Total number of evaluations")
    date_range: dict = Field(..., description="Date range of evaluations")
    average_scores: dict = Field(..., description="Average scores by metric")
    score_distribution: dict = Field(..., description="Distribution of scores")
    category_performance: dict = Field(..., description="Performance by category")
    trends: List[MetricsTrend] = Field(..., description="Trends over time")
    
    class Config:
        schema_extra = {
            "example": {
                "total_evaluations": 100,
                "date_range": {
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-15"
                },
                "average_scores": {
                    "correctness": 0.85,
                    "relevance": 0.90,
                    "completeness": 0.80,
                    "overall": 0.85
                },
                "score_distribution": {
                    "0.0-0.2": 2,
                    "0.2-0.4": 5,
                    "0.4-0.6": 15,
                    "0.6-0.8": 30,
                    "0.8-1.0": 48
                },
                "category_performance": {
                    "authentication": 0.88,
                    "api_usage": 0.82,
                    "troubleshooting": 0.85
                }
            }
        }