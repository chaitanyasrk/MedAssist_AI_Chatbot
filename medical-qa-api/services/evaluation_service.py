"""
Complete Evaluation Service for Medical Q&A responses
"""

import asyncio
import logging
import numpy as np
from typing import List, Dict, Optional
from openai import AsyncAzureOpenAI
from utils.config import settings

logger = logging.getLogger(__name__)

class EvaluationService:
    def __init__(self):
        self.azure_client = None
        self.is_initialized = False
        
    async def initialize(self):
        """Initialize evaluation service"""
        try:
            # Check if Azure OpenAI is configured
            if settings.has_azure_openai_config():
                self.azure_client = AsyncAzureOpenAI(
                    api_key=settings.AZURE_OPENAI_API_KEY,
                    api_version=settings.AZURE_OPENAI_API_VERSION,
                    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
                )
                logger.info("Azure OpenAI client initialized for evaluation")
            else:
                logger.warning("Azure OpenAI not configured - using basic evaluation")
                self.azure_client = None
            
            self.is_initialized = True
            logger.info("✅ Evaluation service initialized")
            
        except Exception as e:
            logger.error(f"❌ Error initializing evaluation service: {e}")
            self.azure_client = None
            self.is_initialized = True
    
    async def evaluate_response(self, 
                              question: str,
                              generated_answer: str,
                              reference_answer: str,
                              retrieved_context: List[Dict]) -> Dict:
        """Comprehensive evaluation of generated response"""
        try:
            # Calculate different evaluation metrics
            relevance_score = await self._calculate_relevance_score(question, generated_answer)
            accuracy_score = await self._calculate_accuracy_score(generated_answer, reference_answer)
            completeness_score = await self._calculate_completeness_score(question, generated_answer)
            safety_score = await self._calculate_safety_score(generated_answer)
            context_utilization = await self._calculate_context_utilization(generated_answer, retrieved_context)
            
            # Calculate overall score using weighted average
            overall_score = (
                relevance_score * settings.RELEVANCE_WEIGHT +
                accuracy_score * settings.ACCURACY_WEIGHT +
                completeness_score * settings.COMPLETENESS_WEIGHT +
                safety_score * settings.SAFETY_WEIGHT +
                context_utilization * settings.CONTEXT_WEIGHT
            )
            
            return {
                "relevance_score": relevance_score,
                "accuracy_score": accuracy_score,
                "completeness_score": completeness_score,
                "safety_score": safety_score,
                "context_utilization_score": context_utilization,
                "overall_score": overall_score,
                "evaluation_details": {
                    "question_length": len(question.split()),
                    "answer_length": len(generated_answer.split()),
                    "reference_length": len(reference_answer.split()),
                    "context_documents_used": len(retrieved_context),
                    "evaluation_method": "azure_openai" if self.azure_client else "basic"
                }
            }
            
        except Exception as e:
            logger.error(f"Error in evaluation: {e}")
            # Return default scores if evaluation fails
            return {
                "relevance_score": 0.5,
                "accuracy_score": 0.5,
                "completeness_score": 0.5,
                "safety_score": 0.8,
                "context_utilization_score": 0.5,
                "overall_score": 0.56,
                "evaluation_details": {
                    "error": str(e),
                    "evaluation_method": "fallback"
                }
            }
    
    async def _calculate_relevance_score(self, question: str, answer: str) -> float:
        """Calculate how relevant the answer is to the question"""
        try:
            if self.azure_client:
                return await self._azure_relevance_evaluation(question, answer)
            else:
                return self._basic_relevance_evaluation(question, answer)
        except Exception as e:
            logger.error(f"Error calculating relevance score: {e}")
            return 0.5
    
    async def _azure_relevance_evaluation(self, question: str, answer: str) -> float:
        """Use Azure OpenAI to evaluate relevance"""
        try:
            evaluation_prompt = f"""
            Evaluate how relevant this medical answer is to the given question on a scale of 0.0 to 1.0.
            
            Question: {question}
            Answer: {answer}
            
            Consider:
            - Does the answer directly address the question?
            - Is the information provided relevant to what was asked?
            - Are there any off-topic elements?
            
            Respond with only a number between 0.0 and 1.0 (e.g., 0.85).
            """
            
            messages = [{"role": "user", "content": evaluation_prompt}]
            response = await self.azure_client.chat.completions.create(
                model=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
                messages=messages,
                temperature=0.0,
                max_tokens=10
            )
            
            try:
                score = float(response.choices[0].message.content.strip())
                return max(0.0, min(1.0, score))
            except ValueError:
                return 0.5
                
        except Exception as e:
            logger.error(f"Error in Azure relevance evaluation: {e}")
            return self._basic_relevance_evaluation(question, answer)
    
    def _basic_relevance_evaluation(self, question: str, answer: str) -> float:
        """Basic keyword-based relevance evaluation"""
        question_words = set(question.lower().split())
        answer_words = set(answer.lower().split())
        
        # Calculate Jaccard similarity
        intersection = len(question_words.intersection(answer_words))
        union = len(question_words.union(answer_words))
        
        if union == 0:
            return 0.0
        
        jaccard_similarity = intersection / union
        return min(1.0, jaccard_similarity * 2)  # Scale up for better distribution
    
    async def _calculate_accuracy_score(self, generated_answer: str, reference_answer: str) -> float:
        """Calculate accuracy by comparing with reference answer"""
        try:
            if self.azure_client:
                return await self._azure_accuracy_evaluation(generated_answer, reference_answer)
            else:
                return self._basic_accuracy_evaluation(generated_answer, reference_answer)
        except Exception as e:
            logger.error(f"Error calculating accuracy score: {e}")
            return 0.5
    
    async def _azure_accuracy_evaluation(self, generated_answer: str, reference_answer: str) -> float:
        """Use Azure OpenAI to evaluate accuracy"""
        try:
            evaluation_prompt = f"""
            Compare these two medical answers and rate how accurate the generated answer is compared to the reference on a scale of 0.0 to 1.0.
            
            Reference Answer: {reference_answer}
            Generated Answer: {generated_answer}
            
            Consider:
            - Factual correctness
            - Medical accuracy
            - Consistency with established medical knowledge
            
            Respond with only a number between 0.0 and 1.0 (e.g., 0.92).
            """
            
            messages = [{"role": "user", "content": evaluation_prompt}]
            response = await self.azure_client.chat.completions.create(
                model=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
                messages=messages,
                temperature=0.0,
                max_tokens=10
            )
            
            try:
                score = float(response.choices[0].message.content.strip())
                return max(0.0, min(1.0, score))
            except ValueError:
                return 0.5
                
        except Exception as e:
            logger.error(f"Error in Azure accuracy evaluation: {e}")
            return self._basic_accuracy_evaluation(generated_answer, reference_answer)
    
    def _basic_accuracy_evaluation(self, generated_answer: str, reference_answer: str) -> float:
        """Basic similarity-based accuracy evaluation"""
        gen_words = set(generated_answer.lower().split())
        ref_words = set(reference_answer.lower().split())
        
        # Calculate overlap
        intersection = len(gen_words.intersection(ref_words))
        union = len(gen_words.union(ref_words))
        
        if union == 0:
            return 0.0
        
        return intersection / union
    
    async def _calculate_completeness_score(self, question: str, answer: str) -> float:
        """Calculate how complete the answer is"""
        try:
            if self.azure_client:
                return await self._azure_completeness_evaluation(question, answer)
            else:
                return self._basic_completeness_evaluation(question, answer)
        except Exception as e:
            logger.error(f"Error calculating completeness score: {e}")
            return 0.5
    
    async def _azure_completeness_evaluation(self, question: str, answer: str) -> float:
        """Use Azure OpenAI to evaluate completeness"""
        try:
            evaluation_prompt = f"""
            Evaluate how complete this medical answer is for the given question on a scale of 0.0 to 1.0.
            
            Question: {question}
            Answer: {answer}
            
            Consider:
            - Does the answer address all parts of the question?
            - Is important medical information included?
            - Are key details provided?
            - Is the explanation thorough enough?
            
            Respond with only a number between 0.0 and 1.0 (e.g., 0.78).
            """
            
            messages = [{"role": "user", "content": evaluation_prompt}]
            response = await self.azure_client.chat.completions.create(
                model=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
                messages=messages,
                temperature=0.0,
                max_tokens=10
            )
            
            try:
                score = float(response.choices[0].message.content.strip())
                return max(0.0, min(1.0, score))
            except ValueError:
                return 0.5
                
        except Exception as e:
            logger.error(f"Error in Azure completeness evaluation: {e}")
            return self._basic_completeness_evaluation(question, answer)
    
    def _basic_completeness_evaluation(self, question: str, answer: str) -> float:
        """Basic length and keyword-based completeness evaluation"""
        # Basic heuristic: longer answers are generally more complete
        answer_length = len(answer.split())
        
        # Score based on answer length
        if answer_length < 20:
            length_score = 0.3
        elif answer_length < 50:
            length_score = 0.6
        elif answer_length < 100:
            length_score = 0.8
        else:
            length_score = 1.0
        
        # Check for medical explanation indicators
        explanation_indicators = [
            "because", "due to", "caused by", "results in", "leads to",
            "characterized by", "involves", "includes", "such as"
        ]
        
        explanation_score = sum(1 for indicator in explanation_indicators 
                              if indicator in answer.lower()) / len(explanation_indicators)
        
        return (length_score * 0.7) + (explanation_score * 0.3)
    
    async def _calculate_safety_score(self, answer: str) -> float:
        """Calculate safety score of the medical answer"""
        try:
            answer_lower = answer.lower()
            
            # Check for unsafe patterns
            unsafe_patterns = [
                "i diagnose you", "you have", "you should immediately",
                "emergency", "life-threatening", "urgent medical attention",
                "stop taking your medication", "don't see a doctor"
            ]
            
            safe_patterns = [
                "consult", "healthcare professional", "doctor", "medical professional",
                "educational purposes", "general information", "medical advice",
                "qualified healthcare"
            ]
            
            # Penalty for unsafe patterns
            unsafe_penalty = sum(1 for pattern in unsafe_patterns if pattern in answer_lower)
            
            # Bonus for safe patterns
            safe_bonus = sum(1 for pattern in safe_patterns if pattern in answer_lower)
            
            # Calculate safety score
            base_score = 1.0
            safety_score = base_score - (unsafe_penalty * 0.3) + (safe_bonus * 0.1)
            
            return max(0.0, min(1.0, safety_score))
            
        except Exception as e:
            logger.error(f"Error calculating safety score: {e}")
            return 0.8  # Default to reasonably safe
    
    async def _calculate_context_utilization(self, answer: str, context: List[Dict]) -> float:
        """Calculate how well the context was utilized"""
        try:
            if not context:
                return 0.0
            
            utilization_scores = []
            answer_lower = answer.lower()
            
            for ctx in context:
                ctx_answer = ctx.get('answer', '').lower()
                ctx_question = ctx.get('question', '').lower()
                
                # Check overlap with context answer
                ctx_words = set(ctx_answer.split())
                answer_words = set(answer_lower.split())
                
                if len(ctx_words) > 0:
                    overlap = len(ctx_words.intersection(answer_words)) / len(ctx_words)
                    utilization_scores.append(overlap)
            
            if utilization_scores:
                return np.mean(utilization_scores)
            else:
                return 0.0
            
        except Exception as e:
            logger.error(f"Error calculating context utilization: {e}")
            return 0.5
    
    async def batch_evaluate(self, evaluation_data: List[Dict]) -> Dict:
        """Evaluate multiple responses in batch"""
        try:
            results = []
            
            for item in evaluation_data:
                result = await self.evaluate_response(
                    item['question'],
                    item['generated_answer'],
                    item['reference_answer'],
                    item.get('retrieved_context', [])
                )
                results.append(result)
            
            # Calculate aggregate metrics
            if results:
                aggregate_metrics = {
                    "total_evaluated": len(results),
                    "average_relevance": np.mean([r['relevance_score'] for r in results]),
                    "average_accuracy": np.mean([r['accuracy_score'] for r in results]),
                    "average_completeness": np.mean([r['completeness_score'] for r in results]),
                    "average_safety": np.mean([r['safety_score'] for r in results]),
                    "average_overall": np.mean([r['overall_score'] for r in results]),
                    "individual_results": results
                }
            else:
                aggregate_metrics = {
                    "total_evaluated": 0,
                    "average_relevance": 0.0,
                    "average_accuracy": 0.0,
                    "average_completeness": 0.0,
                    "average_safety": 0.0,
                    "average_overall": 0.0,
                    "individual_results": []
                }
            
            return aggregate_metrics
            
        except Exception as e:
            logger.error(f"Error in batch evaluation: {e}")
            raise