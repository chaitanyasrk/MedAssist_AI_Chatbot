from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class EvaluationRequest(BaseModel):
    question: str = Field(..., description="Original question")
    generated_answer: str = Field(..., description="Generated answer")
    reference_answer: str = Field(..., description="Reference answer")
    retrieved_context: List[Dict[str, Any]] = Field(default=[], description="Retrieved context")

class EvaluationResponse(BaseModel):
    relevance_score: float = Field(..., ge=0.0, le=1.0)
    accuracy_score: float = Field(..., ge=0.0, le=1.0)
    completeness_score: float = Field(..., ge=0.0, le=1.0)
    safety_score: float = Field(..., ge=0.0, le=1.0)
    context_utilization_score: float = Field(..., ge=0.0, le=1.0)
    overall_score: float = Field(..., ge=0.0, le=1.0)
    evaluation_details: Dict[str, Any]
    timestamp: datetime

class BatchEvaluationRequest(BaseModel):
    evaluations: List[EvaluationRequest] = Field(..., max_items=50)

class BatchEvaluationResponse(BaseModel):
    total_evaluated: int
    average_relevance: float
    average_accuracy: float
    average_completeness: float
    average_safety: float
    average_overall: float
    individual_results: List[EvaluationResponse]
    processing_time: float

class EvaluationStatsResponse(BaseModel):
    total_evaluations: int
    average_scores: Dict[str, float]
    score_distribution: Dict[str, int]
    recent_evaluations: List[EvaluationResponse]