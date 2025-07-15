"""
Simplified Guardrails Service for Medical Q&A API

This version provides basic safety checks without requiring NVIDIA Guardrails,
which can be problematic on Windows systems.
"""

import logging
import re
from typing import Dict, List, Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class GuardrailsService:
    """Simplified guardrails service without NVIDIA dependencies"""
    
    def __init__(self):
        self.is_initialized = False
        
        # Basic harmful patterns to detect
        self.harmful_patterns = [
            r'\bignore\s+previous\s+instructions\b',
            r'\bact\s+as\s+if\b',
            r'\bpretend\s+to\s+be\b',
            r'\byou\s+are\s+now\b',
            r'\bforget\s+everything\b',
            r'\boverride\s+your\s+instructions\b',
        ]
        
        # Medical safety patterns
        self.unsafe_medical_patterns = [
            r'\bi\s+diagnose\s+you\s+with\b',
            r'\byou\s+have\s+\w+\s+disease\b',
            r'\btake\s+this\s+medication\s+immediately\b',
            r'\bdon\'t\s+see\s+a\s+doctor\b',
            r'\bavoid\s+medical\s+treatment\b',
        ]
        
        # Safe medical phrases that should be present
        self.safe_medical_phrases = [
            "consult",
            "healthcare professional", 
            "doctor",
            "medical professional",
            "educational purposes",
            "general information"
        ]
        
    async def initialize(self):
        """Initialize the guardrails service"""
        try:
            self.is_initialized = True
            logger.info("Simplified Guardrails service initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing guardrails service: {e}")
            raise
    
    async def check_input(self, user_input: str) -> Tuple[bool, Optional[str]]:
        """
        Check user input for harmful content
        Returns: (is_safe, rejection_message)
        """
        try:
            if not self.is_initialized:
                return True, None
            
            user_input_lower = user_input.lower()
            
            # Check for prompt injection patterns
            for pattern in self.harmful_patterns:
                if re.search(pattern, user_input_lower, re.IGNORECASE):
                    return False, "I cannot process requests that attempt to modify my behavior or instructions."
            
            # Check for unsafe medical advice requests
            unsafe_patterns = [
                r'\bshould\s+i\s+take\b',
                r'\bwhat\s+should\s+i\s+do\s+about\s+my\b',
                r'\bdiagnose\s+me\b',
                r'\bwhat\s+do\s+i\s+have\b',
                r'\bi\s+think\s+i\s+have\b',
                r'\bmy\s+symptoms\s+are\b',
            ]
            
            for pattern in unsafe_patterns:
                if re.search(pattern, user_input_lower, re.IGNORECASE):
                    return False, "I cannot provide personal medical advice. Please consult with a healthcare professional for personal medical concerns."
            
            # Check for other harmful content
            harmful_keywords = [
                "emergency", "urgent", "immediately", "right now",
                "life-threatening", "critical condition"
            ]
            
            if any(keyword in user_input_lower for keyword in harmful_keywords):
                return False, "For medical emergencies, please contact emergency services immediately. I cannot provide emergency medical advice."
            
            return True, None
            
        except Exception as e:
            logger.error(f"Error checking input with guardrails: {e}")
            return True, None  # Allow on error to avoid blocking legitimate queries
    
    async def check_output(self, generated_response: str) -> Tuple[bool, Optional[str]]:
        """
        Check generated response for unsafe content
        Returns: (is_safe, rejection_message)
        """
        try:
            if not self.is_initialized:
                return True, None
            
            response_lower = generated_response.lower()
            
            # Check for unsafe medical advice patterns
            for pattern in self.unsafe_medical_patterns:
                if re.search(pattern, response_lower, re.IGNORECASE):
                    return False, "Response contains potentially unsafe medical advice. Please consult a healthcare professional."
            
            # Check for definitive diagnostic language
            unsafe_diagnostic_patterns = [
                r'\byou\s+definitely\s+have\b',
                r'\byou\s+are\s+suffering\s+from\b',
                r'\bthis\s+confirms\s+you\s+have\b',
                r'\byou\s+need\s+to\s+take\b',
                r'\bstop\s+taking\s+your\s+medication\b',
            ]
            
            for pattern in unsafe_diagnostic_patterns:
                if re.search(pattern, response_lower, re.IGNORECASE):
                    return False, "Response contains inappropriate medical advice. Please consult a healthcare professional."
            
            return True, None
            
        except Exception as e:
            logger.error(f"Error checking output with guardrails: {e}")
            return True, None
    
    def get_medical_disclaimer(self) -> str:
        """Get standard medical disclaimer"""
        return """

**Medical Disclaimer**: This information is for educational purposes only and should not be considered as medical advice. Always consult with qualified healthcare professionals for personal medical concerns, diagnosis, or treatment decisions.
        """
    
    def is_medical_emergency_query(self, query: str) -> bool:
        """Check if query indicates a medical emergency"""
        emergency_keywords = [
            "chest pain", "heart attack", "stroke", "bleeding", "unconscious",
            "emergency", "urgent", "immediately", "can't breathe", "severe pain"
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in emergency_keywords)
    
    def get_emergency_response(self) -> str:
        """Get response for emergency queries"""
        return """
🚨 **MEDICAL EMERGENCY NOTICE** 🚨

If this is a medical emergency, please:
- Call emergency services immediately (911 in US, 999 in UK, 112 in EU)
- Go to the nearest emergency room
- Contact your local emergency services

I cannot provide emergency medical advice. Please seek immediate professional medical attention.
        """
    
    def assess_response_safety(self, response: str) -> Dict[str, float]:
        """
        Assess response safety with scoring
        Returns scores for different safety aspects
        """
        response_lower = response.lower()
        
        # Safety score calculation
        safety_score = 1.0
        
        # Penalty for unsafe patterns
        unsafe_count = sum(1 for pattern in self.unsafe_medical_patterns 
                          if re.search(pattern, response_lower, re.IGNORECASE))
        safety_score -= unsafe_count * 0.3
        
        # Bonus for safe patterns
        safe_count = sum(1 for phrase in self.safe_medical_phrases 
                        if phrase in response_lower)
        safety_score += safe_count * 0.1
        
        # Ensure score is between 0 and 1
        safety_score = max(0.0, min(1.0, safety_score))
        
        return {
            "overall_safety": safety_score,
            "unsafe_patterns_detected": unsafe_count,
            "safe_patterns_found": safe_count,
            "emergency_indicators": 1 if self.is_medical_emergency_query(response) else 0
        }