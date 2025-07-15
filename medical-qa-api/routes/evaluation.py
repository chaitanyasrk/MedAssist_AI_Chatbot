import asyncio
import logging
import time
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from datetime import datetime

from database.connection import get_db
from database.models import EvaluationResult, ChatMessage
from models.evalution_models import (
    EvaluationRequest, EvaluationResponse,
    BatchEvaluationRequest, BatchEvaluationResponse,
    EvaluationStatsResponse
)
from services.evaluation_service import EvaluationService
from services.rag_service import MedicalRAGService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/evaluation", tags=["evaluation"])

# Global service instances
evaluation_service = EvaluationService()
rag_service = MedicalRAGService()

@router.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    await evaluation_service.initialize()
    await rag_service.initialize()

@router.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_response(
    request: EvaluationRequest,
    db: AsyncSession = Depends(get_db)
):
    """Evaluate a single response"""
    try:
        start_time = time.time()
        
        # Perform evaluation
        eval_result = await evaluation_service.evaluate_response(
            request.question,
            request.generated_answer,
            request.reference_answer,
            request.retrieved_context
        )
        
        # Save evaluation result to database
        evaluation_record = EvaluationResult(
            message_id=0,  # Could be linked to actual message if provided
            relevance_score=eval_result["relevance_score"],
            accuracy_score=eval_result["accuracy_score"],
            completeness_score=eval_result["completeness_score"],
            safety_score=eval_result["safety_score"],
            overall_score=eval_result["overall_score"],
            evaluation_method="automated",
            reference_answer=request.reference_answer
        )
        
        db.add(evaluation_record)
        await db.commit()
        
        return EvaluationResponse(
            relevance_score=eval_result["relevance_score"],
            accuracy_score=eval_result["accuracy_score"],
            completeness_score=eval_result["completeness_score"],
            safety_score=eval_result["safety_score"],
            context_utilization_score=eval_result["context_utilization_score"],
            overall_score=eval_result["overall_score"],
            evaluation_details=eval_result["evaluation_details"],
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Error in evaluation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to evaluate response"
        )

@router.post("/batch-evaluate", response_model=BatchEvaluationResponse)
async def batch_evaluate_responses(
    request: BatchEvaluationRequest,
    db: AsyncSession = Depends(get_db)
):
    """Evaluate multiple responses in batch"""
    try:
        start_time = time.time()
        
        # Prepare evaluation data
        evaluation_data = []
        for eval_req in request.evaluations:
            evaluation_data.append({
                "question": eval_req.question,
                "generated_answer": eval_req.generated_answer,
                "reference_answer": eval_req.reference_answer,
                "retrieved_context": eval_req.retrieved_context
            })
        
        # Perform batch evaluation
        batch_result = await evaluation_service.batch_evaluate(evaluation_data)
        
        # Save evaluation results
        evaluation_records = []
        for i, result in enumerate(batch_result["individual_results"]):
            record = EvaluationResult(
                message_id=0,
                relevance_score=result["relevance_score"],
                accuracy_score=result["accuracy_score"],
                completeness_score=result["completeness_score"],
                safety_score=result["safety_score"],
                overall_score=result["overall_score"],
                evaluation_method="batch_automated",
                reference_answer=request.evaluations[i].reference_answer
            )
            evaluation_records.append(record)
        
        db.add_all(evaluation_records)
        await db.commit()
        
        processing_time = time.time() - start_time
        
        # Convert individual results to response format
        individual_responses = []
        for result in batch_result["individual_results"]:
            individual_responses.append(EvaluationResponse(
                relevance_score=result["relevance_score"],
                accuracy_score=result["accuracy_score"],
                completeness_score=result["completeness_score"],
                safety_score=result["safety_score"],
                context_utilization_score=result["context_utilization_score"],
                overall_score=result["overall_score"],
                evaluation_details=result["evaluation_details"],
                timestamp=datetime.utcnow()
            ))
        
        return BatchEvaluationResponse(
            total_evaluated=batch_result["total_evaluated"],
            average_relevance=batch_result["average_relevance"],
            average_accuracy=batch_result["average_accuracy"],
            average_completeness=batch_result["average_completeness"],
            average_safety=batch_result["average_safety"],
            average_overall=batch_result["average_overall"],
            individual_results=individual_responses,
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"Error in batch evaluation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to perform batch evaluation"
        )

@router.get("/stats", response_model=EvaluationStatsResponse)
async def get_evaluation_stats(
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """Get evaluation statistics"""
    try:
        # Get total evaluations count
        total_count = await db.scalar(select(func.count(EvaluationResult.id)))
        
        # Get average scores
        avg_query = select(
            func.avg(EvaluationResult.relevance_score).label('avg_relevance'),
            func.avg(EvaluationResult.accuracy_score).label('avg_accuracy'),
            func.avg(EvaluationResult.completeness_score).label('avg_completeness'),
            func.avg(EvaluationResult.safety_score).label('avg_safety'),
            func.avg(EvaluationResult.overall_score).label('avg_overall')
        )
        avg_result = await db.execute(avg_query)
        avg_scores = avg_result.first()
        
        # Get recent evaluations
        recent_query = select(EvaluationResult).order_by(
            desc(EvaluationResult.created_at)
        ).limit(limit)
        recent_result = await db.execute(recent_query)
        recent_evaluations = recent_result.scalars().all()
        
        # Create score distribution (simple bucketing)
        score_distribution = {
            "excellent (0.8-1.0)": 0,
            "good (0.6-0.8)": 0,
            "fair (0.4-0.6)": 0,
            "poor (0.0-0.4)": 0
        }
        
        # Count score distribution
        for evaluation in recent_evaluations:
            score = evaluation.overall_score
            if score >= 0.8:
                score_distribution["excellent (0.8-1.0)"] += 1
            elif score >= 0.6:
                score_distribution["good (0.6-0.8)"] += 1
            elif score >= 0.4:
                score_distribution["fair (0.4-0.6)"] += 1
            else:
                score_distribution["poor (0.0-0.4)"] += 1
        
        # Convert recent evaluations to response format
        recent_eval_responses = []
        for eval_record in recent_evaluations:
            recent_eval_responses.append(EvaluationResponse(
                relevance_score=eval_record.relevance_score,
                accuracy_score=eval_record.accuracy_score,
                completeness_score=eval_record.completeness_score,
                safety_score=eval_record.safety_score,
                context_utilization_score=0.0,  # Not stored separately
                overall_score=eval_record.overall_score,
                evaluation_details={},
                timestamp=eval_record.created_at
            ))
        
        return EvaluationStatsResponse(
            total_evaluations=total_count or 0,
            average_scores={
                "relevance": float(avg_scores.avg_relevance or 0),
                "accuracy": float(avg_scores.avg_accuracy or 0),
                "completeness": float(avg_scores.avg_completeness or 0),
                "safety": float(avg_scores.avg_safety or 0),
                "overall": float(avg_scores.avg_overall or 0)
            },
            score_distribution=score_distribution,
            recent_evaluations=recent_eval_responses
        )
        
    except Exception as e:
        logger.error(f"Error getting evaluation stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve evaluation statistics"
        )

@router.post("/evaluate-dataset")
async def evaluate_against_dataset(
    sample_size: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """Evaluate model against evaluation dataset"""
    try:
        # Get evaluation dataset
        eval_dataset = await rag_service.get_evaluation_dataset()
        
        # Limit sample size
        sample_data = eval_dataset[:sample_size]
        
        # Process each sample
        evaluation_results = []
        for item in sample_data:
            try:
                # Generate response using RAG
                rag_result = await rag_service.process_query(item['question'], "eval_session")
                
                if rag_result["evaluation_ready"]:
                    # Evaluate the response
                    eval_result = await evaluation_service.evaluate_response(
                        item['question'],
                        rag_result['response'],
                        item['answer'],
                        rag_result['retrieved_context']
                    )
                    
                    evaluation_results.append({
                        "question": item['question'],
                        "generated_answer": rag_result['response'],
                        "reference_answer": item['answer'],
                        "evaluation": eval_result
                    })
                    
            except Exception as e:
                logger.warning(f"Failed to evaluate item: {e}")
                continue
        
        # Calculate aggregate statistics
        if evaluation_results:
            avg_scores = {
                "relevance": sum(r['evaluation']['relevance_score'] for r in evaluation_results) / len(evaluation_results),
                "accuracy": sum(r['evaluation']['accuracy_score'] for r in evaluation_results) / len(evaluation_results),
                "completeness": sum(r['evaluation']['completeness_score'] for r in evaluation_results) / len(evaluation_results),
                "safety": sum(r['evaluation']['safety_score'] for r in evaluation_results) / len(evaluation_results),
                "overall": sum(r['evaluation']['overall_score'] for r in evaluation_results) / len(evaluation_results)
            }
        else:
            avg_scores = {"relevance": 0, "accuracy": 0, "completeness": 0, "safety": 0, "overall": 0}
        
        return {
            "total_evaluated": len(evaluation_results),
            "sample_size": sample_size,
            "average_scores": avg_scores,
            "detailed_results": evaluation_results[:10]  # Return first 10 for brevity
        }
        
    except Exception as e:
        logger.error(f"Error evaluating against dataset: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to evaluate against dataset"
        )