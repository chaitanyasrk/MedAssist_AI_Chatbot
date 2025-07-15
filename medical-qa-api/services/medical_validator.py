import re
import logging
from typing import List, Dict, Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)

class MedicalQueryType(Enum):
    DIAGNOSIS = "diagnosis"
    TREATMENT = "treatment"
    MEDICATION = "medication"
    ANATOMY = "anatomy"
    PHYSIOLOGY = "physiology"
    PATHOLOGY = "pathology"
    GENERAL = "general"
    INVALID = "invalid"

class MedicalValidator:
    def __init__(self):
        self.medical_keywords = {
            "diagnosis": [
                "diagnose", "diagnosis", "symptom", "symptoms", "condition", 
                "disease", "disorder", "syndrome", "infection", "cancer",
                "tumor", "malignancy", "pathology", "clinical", "medical"
            ],
            "treatment": [
                "treatment", "therapy", "procedure", "surgery", "intervention",
                "management", "care", "protocol", "guidelines", "approach"
            ],
            "medication": [
                "drug", "medication", "medicine", "pharmaceutical", "dosage",
                "prescription", "administration", "side effects", "contraindication"
            ],
            "anatomy": [
                "anatomy", "anatomical", "organ", "tissue", "cell", "system",
                "structure", "bone", "muscle", "blood", "heart", "brain"
            ],
            "physiology": [
                "physiology", "physiological", "function", "mechanism", "process",
                "metabolism", "homeostasis", "regulation", "response"
            ]
        }
        
        self.non_medical_keywords = [
            "weather", "sports", "politics", "cooking", "travel", "entertainment",
            "technology", "programming", "business", "finance", "music", "art",
            "literature", "history", "geography", "mathematics", "physics",
            "chemistry", "engineering", "legal", "law"
        ]
    
    def validate_medical_query(self, query: str) -> Tuple[bool, MedicalQueryType, float]:
        """
        Validate if query is medical-related
        Returns: (is_medical, query_type, confidence_score)
        """
        query_lower = query.lower()
        
        # Check for non-medical keywords
        non_medical_score = self._calculate_non_medical_score(query_lower)
        if non_medical_score > 0.3:
            return False, MedicalQueryType.INVALID, 1.0 - non_medical_score
        
        # Calculate medical scores for each category
        medical_scores = {}
        for category, keywords in self.medical_keywords.items():
            score = self._calculate_keyword_score(query_lower, keywords)
            medical_scores[category] = score
        
        # Get best matching category
        best_category = max(medical_scores, key=medical_scores.get)
        best_score = medical_scores[best_category]
        
        # Determine if query is medical
        is_medical = best_score > 0.1 or self._has_medical_patterns(query_lower)
        
        if is_medical:
            query_type = MedicalQueryType(best_category)
            confidence = min(best_score * 2, 1.0)  # Scale confidence
        else:
            query_type = MedicalQueryType.INVALID
            confidence = 0.0
        
        return is_medical, query_type, confidence
    
    def _calculate_keyword_score(self, query: str, keywords: List[str]) -> float:
        """Calculate relevance score based on keyword presence"""
        query_words = set(query.split())
        keyword_matches = sum(1 for keyword in keywords if keyword in query)
        return keyword_matches / len(keywords)
    
    def _calculate_non_medical_score(self, query: str) -> float:
        """Calculate score for non-medical content"""
        query_words = set(query.split())
        non_medical_matches = sum(1 for keyword in self.non_medical_keywords if keyword in query)
        return non_medical_matches / len(self.non_medical_keywords)
    
    def _has_medical_patterns(self, query: str) -> bool:
        """Check for medical patterns in query"""
        medical_patterns = [
            r'\b(what|how|why|when|where)\s+(is|are|do|does|can|will)\s+.*\b(disease|condition|symptom|treatment|drug|medication|therapy|diagnosis)\b',
            r'\b(diagnose|treat|cure|prevent|manage)\b',
            r'\b(patient|doctor|physician|nurse|hospital|clinic|medical)\b',
            r'\b(mg|ml|tablet|capsule|injection|IV|oral|topical)\b',
            r'\b(pain|fever|infection|inflammation|bleeding|swelling)\b'
        ]
        
        for pattern in medical_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                return True
        return False
    
    def get_rejection_message(self, query_type: MedicalQueryType) -> str:
        """Get appropriate rejection message for non-medical queries"""
        messages = {
            MedicalQueryType.INVALID: "I'm sorry, but I can only answer medical and healthcare-related questions. Please ask about medical conditions, treatments, medications, anatomy, or physiology.",
            "general": "I'm a specialized medical assistant. Please ask questions related to medicine, healthcare, diseases, treatments, or medical procedures."
        }
        
        return messages.get(query_type, messages["general"])
    
    def is_safe_medical_query(self, query: str) -> Tuple[bool, Optional[str]]:
        """Check if medical query is safe (no personal medical advice)"""
        unsafe_patterns = [
            r'\b(should i|what should i|i have|i am experiencing|i feel|my)\b',
            r'\b(diagnose me|what do i have|am i)\b',
            r'\b(emergency|urgent|immediately|right now)\b'
        ]
        
        for pattern in unsafe_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                return False, "I cannot provide personal medical advice. Please consult with a healthcare professional for personal medical concerns."
        
        return True, None