"""
Evaluation service for measuring response quality and metrics
"""

import json
import logging
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import difflib
from dataclasses import dataclass

from openai import AzureOpenAI
from config.settings import settings
from models.evalution_models import EvaluationMetrics, GoldenExample

logger = logging.getLogger(__name__)


@dataclass
class EvaluationResult:
    """Single evaluation result"""
    query: str
    generated_response: str
    expected_response: str
    correctness_score: float
    relevance_score: float
    completeness_score: float
    overall_score: float
    timestamp: datetime


class EvaluationService:
    """Service for evaluating response quality"""
    
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            azure_endpoint=settings.azure_openai_endpoint
        )
        
        self.golden_dataset = self._load_golden_dataset()
        self.evaluation_history: List[EvaluationResult] = []
        
        # Ensure data directory exists
        os.makedirs("./data", exist_ok=True)
    
    def _load_golden_dataset(self) -> List[GoldenExample]:
        """Load golden dataset for evaluation"""
        try:
            if os.path.exists(settings.golden_dataset_path):
                with open(settings.golden_dataset_path, 'r') as f:
                    data = json.load(f)
                    return [GoldenExample(**item) for item in data]
            else:
                # Create default golden dataset
                golden_data = self._create_default_golden_dataset()
                self._save_golden_dataset(golden_data)
                return golden_data
        except Exception as e:
            logger.error(f"Error loading golden dataset: {str(e)}")
            return self._create_default_golden_dataset()
    
    def _create_default_golden_dataset(self) -> List[GoldenExample]:
        """Create default golden dataset"""
        return [
            GoldenExample(
                query="How do I fix 401 authentication errors?",
                expected_response="For 401 authentication errors, check these steps: 1. Verify your bearer token is not expired, 2. Ensure the token format is correct: 'Bearer <token>', 3. Check that the token has required scopes, 4. If issues persist, regenerate your token",
                category="authentication",
                difficulty="easy",
                context_keywords=["401", "authentication", "bearer token", "unauthorized"]
            ),
            GoldenExample(
                query="What's the payload structure for creating a quote?",
                expected_response="To create a quote using the Quote Management API, use the POST /api/v1/quotes endpoint with this payload structure: accountId (required), opportunityId (required), and products array with productId, quantity, and listPrice",
                category="api_usage",
                difficulty="medium",
                context_keywords=["quote", "payload", "POST", "api", "structure"]
            ),
            GoldenExample(
                query="How to handle rate limiting in API calls?",
                expected_response="For 429 Rate Limit Exceeded errors: 1. Implement exponential backoff in retry logic, 2. Reduce request frequency, 3. Consider caching responses, 4. Contact support for higher rate limits if needed",
                category="troubleshooting",
                difficulty="medium",
                context_keywords=["rate limit", "429", "backoff", "retry", "frequency"]
            ),
            GoldenExample(
                query="What headers are required for the pricing API?",
                expected_response="The Pricing Engine API (POST /api/v1/pricing/calculate) requires these headers: Authorization: Bearer <token> and Content-Type: application/json",
                category="api_usage",
                difficulty="easy",
                context_keywords=["headers", "pricing", "authorization", "content-type"]
            ),
            GoldenExample(
                query="How do I troubleshoot 500 internal server errors?",
                expected_response="For 500 Internal Server Error: 1. Retry request after delay, 2. Check API status page, 3. Contact technical support, 4. Check if it's a temporary server issue",
                category="troubleshooting",
                difficulty="hard",
                context_keywords=["500", "internal server error", "retry", "status", "support"]
            ),
            GoldenExample(
                query="What's the difference between 404 and 403 errors?",
                expected_response="404 Not Found means the resource doesn't exist or can't be found. 403 Forbidden means the resource exists but you don't have permission to access it. Check resource ID for 404, check permissions for 403.",
                category="troubleshooting",
                difficulty="medium",
                context_keywords=["404", "403", "not found", "forbidden", "permissions"]
            )
        ]
    
    def _save_golden_dataset(self, dataset: List[GoldenExample]):
        """Save golden dataset to file"""
        try:
            data = [example.dict() for example in dataset]
            with open(settings.golden_dataset_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving golden dataset: {str(e)}")
    
    async def evaluate_response(
        self,
        query: str,
        generated_response: str,
        expected_response: Optional[str] = None
    ) -> EvaluationMetrics:
        """Evaluate a generated response against expected response"""
        try:
            # Find expected response from golden dataset if not provided
            if not expected_response:
                expected_response = self._find_expected_response(query)
            
            if not expected_response:
                # If no golden example found, use AI-based evaluation
                return await self._ai_based_evaluation(query, generated_response)
            
            # Calculate different metrics
            correctness_score = await self._calculate_correctness(
                query, generated_response, expected_response
            )
            relevance_score = await self._calculate_relevance(query, generated_response)
            completeness_score = await self._calculate_completeness(
                generated_response, expected_response
            )
            
            # Calculate overall score (weighted average)
            overall_score = (
                correctness_score * 0.4 +
                relevance_score * 0.3 +
                completeness_score * 0.3
            )
            
            # Store evaluation result
            eval_result = EvaluationResult(
                query=query,
                generated_response=generated_response,
                expected_response=expected_response,
                correctness_score=correctness_score,
                relevance_score=relevance_score,
                completeness_score=completeness_score,
                overall_score=overall_score,
                timestamp=datetime.utcnow()
            )
            
            self.evaluation_history.append(eval_result)
            
            return EvaluationMetrics(
                correctness_score=correctness_score,
                relevance_score=relevance_score,
                completeness_score=completeness_score,
                overall_score=overall_score,
                evaluation_timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error evaluating response: {str(e)}")
            raise
    
    def _find_expected_response(self, query: str) -> Optional[str]:
        """Find expected response from golden dataset"""
        # Simple keyword matching for now
        query_lower = query.lower()
        
        for example in self.golden_dataset:
            # Check if query contains keywords from the example
            keyword_matches = sum(1 for keyword in example.context_keywords 
                                if keyword.lower() in query_lower)
            
            # If more than half keywords match, consider it a match
            if keyword_matches >= len(example.context_keywords) * 0.5:
                return example.expected_response
        
        return None
    
    async def _calculate_correctness(
        self, 
        query: str, 
        generated: str, 
        expected: str
    ) -> float:
        """Calculate correctness score using AI evaluation"""
        try:
            prompt = f"""
            Evaluate the correctness of the generated response compared to the expected response for the given query.
            
            Query: {query}
            
            Expected Response: {expected}
            
            Generated Response: {generated}
            
            Rate the correctness on a scale of 0.0 to 1.0 where:
            - 1.0 = Completely correct, all information accurate
            - 0.8-0.9 = Mostly correct with minor inaccuracies
            - 0.6-0.7 = Partially correct but missing key information
            - 0.4-0.5 = Some correct information but significant errors
            - 0.0-0.3 = Mostly incorrect or misleading
            
            Respond with only a number between 0.0 and 1.0.
            """
            
            response = self.client.chat.completions.create(
                model=settings.azure_openai_deployment_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=10
            )
            
            score_text = response.choices[0].message.content.strip()
            return float(score_text)
            
        except Exception as e:
            logger.error(f"Error calculating correctness: {str(e)}")
            # Fallback to simple text similarity
            return self._text_similarity(generated, expected)
    
    async def _calculate_relevance(self, query: str, generated: str) -> float:
        """Calculate relevance score"""
        try:
            prompt = f"""
            Evaluate how relevant the generated response is to the user's query.
            
            Query: {query}
            
            Generated Response: {generated}
            
            Rate the relevance on a scale of 0.0 to 1.0 where:
            - 1.0 = Perfectly relevant, directly answers the query
            - 0.8-0.9 = Highly relevant with minor tangents
            - 0.6-0.7 = Somewhat relevant but includes irrelevant information
            - 0.4-0.5 = Partially relevant but misses the main point
            - 0.0-0.3 = Not relevant or off-topic
            
            Respond with only a number between 0.0 and 1.0.
            """
            
            response = self.client.chat.completions.create(
                model=settings.azure_openai_deployment_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=10
            )
            
            score_text = response.choices[0].message.content.strip()
            return float(score_text)
            
        except Exception as e:
            logger.error(f"Error calculating relevance: {str(e)}")
            # Fallback to keyword matching
            query_words = set(query.lower().split())
            response_words = set(generated.lower().split())
            if not query_words:
                return 0.5
            return len(query_words.intersection(response_words)) / len(query_words)
    
    async def _calculate_completeness(self, generated: str, expected: str) -> float:
        """Calculate completeness score"""
        try:
            prompt = f"""
            Evaluate how complete the generated response is compared to the expected response.
            
            Expected Response: {expected}
            
            Generated Response: {generated}
            
            Rate the completeness on a scale of 0.0 to 1.0 where:
            - 1.0 = Covers all important points from expected response
            - 0.8-0.9 = Covers most important points with minor omissions
            - 0.6-0.7 = Covers some important points but missing key elements
            - 0.4-0.5 = Covers few important points, significant gaps
            - 0.0-0.3 = Missing most important information
            
            Respond with only a number between 0.0 and 1.0.
            """
            
            response = self.client.chat.completions.create(
                model=settings.azure_openai_deployment_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=10
            )
            
            score_text = response.choices[0].message.content.strip()
            return float(score_text)
            
        except Exception as e:
            logger.error(f"Error calculating completeness: {str(e)}")
            # Fallback to length ratio
            expected_length = len(expected.split())
            generated_length = len(generated.split())
            if expected_length == 0:
                return 1.0 if generated_length == 0 else 0.5
            return min(generated_length / expected_length, 1.0)
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity using difflib"""
        return difflib.SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    async def _ai_based_evaluation(self, query: str, generated: str) -> EvaluationMetrics:
        """AI-based evaluation when no golden example exists"""
        try:
            prompt = f"""
            Evaluate the quality of this response to a troubleshooting query about Conga CPQ Turbo API.
            
            Query: {query}
            Response: {generated}
            
            Evaluate on these dimensions (respond with only three numbers separated by commas):
            1. Correctness (0.0-1.0): Is the technical information accurate?
            2. Relevance (0.0-1.0): Does it directly address the query?
            3. Completeness (0.0-1.0): Is the response comprehensive enough?
            
            Format: correctness,relevance,completeness
            Example: 0.8,0.9,0.7
            """
            
            response = self.client.chat.completions.create(
                model=settings.azure_openai_deployment_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=20
            )
            
            scores_text = response.choices[0].message.content.strip()
            scores = [float(x.strip()) for x in scores_text.split(',')]
            
            correctness_score, relevance_score, completeness_score = scores
            overall_score = (correctness_score * 0.4 + relevance_score * 0.3 + completeness_score * 0.3)
            
            return EvaluationMetrics(
                correctness_score=correctness_score,
                relevance_score=relevance_score,
                completeness_score=completeness_score,
                overall_score=overall_score,
                evaluation_timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error in AI-based evaluation: {str(e)}")
            # Return neutral scores on error
            return EvaluationMetrics(
                correctness_score=0.5,
                relevance_score=0.5,
                completeness_score=0.5,
                overall_score=0.5,
                evaluation_timestamp=datetime.utcnow()
            )
    
    async def get_overall_metrics(self) -> Dict[str, Any]:
        """Get overall evaluation metrics"""
        if not self.evaluation_history:
            return {
                "total_evaluations": 0,
                "average_scores": {
                    "correctness": 0.0,
                    "relevance": 0.0,
                    "completeness": 0.0,
                    "overall": 0.0
                },
                "score_distribution": {},
                "recent_evaluations": []
            }
        
        # Calculate averages
        total_evaluations = len(self.evaluation_history)
        avg_correctness = sum(e.correctness_score for e in self.evaluation_history) / total_evaluations
        avg_relevance = sum(e.relevance_score for e in self.evaluation_history) / total_evaluations
        avg_completeness = sum(e.completeness_score for e in self.evaluation_history) / total_evaluations
        avg_overall = sum(e.overall_score for e in self.evaluation_history) / total_evaluations
        
        # Score distribution
        score_ranges = {"0.0-0.2": 0, "0.2-0.4": 0, "0.4-0.6": 0, "0.6-0.8": 0, "0.8-1.0": 0}
        for evaluation in self.evaluation_history:
            score = evaluation.overall_score
            if score < 0.2:
                score_ranges["0.0-0.2"] += 1
            elif score < 0.4:
                score_ranges["0.2-0.4"] += 1
            elif score < 0.6:
                score_ranges["0.4-0.6"] += 1
            elif score < 0.8:
                score_ranges["0.6-0.8"] += 1
            else:
                score_ranges["0.8-1.0"] += 1
        
        # Recent evaluations (last 10)
        recent_evaluations = [
            {
                "query": e.query[:100] + "..." if len(e.query) > 100 else e.query,
                "overall_score": e.overall_score,
                "timestamp": e.timestamp.isoformat()
            }
            for e in sorted(self.evaluation_history, key=lambda x: x.timestamp, reverse=True)[:10]
        ]
        
        return {
            "total_evaluations": total_evaluations,
            "average_scores": {
                "correctness": round(avg_correctness, 3),
                "relevance": round(avg_relevance, 3),
                "completeness": round(avg_completeness, 3),
                "overall": round(avg_overall, 3)
            },
            "score_distribution": score_ranges,
            "recent_evaluations": recent_evaluations,
            "last_updated": datetime.utcnow().isoformat()
        }
    
    async def get_golden_dataset(self) -> List[Dict[str, Any]]:
        """Get golden dataset"""
        return [example.dict() for example in self.golden_dataset]
    
    async def add_golden_example(self, example: GoldenExample):
        """Add new golden example"""
        self.golden_dataset.append(example)
        self._save_golden_dataset(self.golden_dataset)
    
    async def export_evaluation_metrics(self) -> Dict[str, Any]:
        """Export evaluation metrics for analysis"""
        return {
            "evaluation_history": [
                {
                    "query": e.query,
                    "generated_response": e.generated_response,
                    "expected_response": e.expected_response,
                    "correctness_score": e.correctness_score,
                    "relevance_score": e.relevance_score,
                    "completeness_score": e.completeness_score,
                    "overall_score": e.overall_score,
                    "timestamp": e.timestamp.isoformat()
                }
                for e in self.evaluation_history
            ],
            "golden_dataset": await self.get_golden_dataset(),
            "overall_metrics": await self.get_overall_metrics()
        }