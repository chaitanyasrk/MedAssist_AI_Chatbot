"""
NVIDIA Guardrails service for input validation and safety
"""

import logging
import re
import os
from typing import List, Dict, Any, Optional
import yaml

logger = logging.getLogger(__name__)


class GuardrailsService:
    """Service for implementing guardrails and input validation"""
    
    def __init__(self):
        self.config = self._load_guardrails_config()
        self.blocked_patterns = self._load_blocked_patterns()
        self.allowed_topics = self._load_allowed_topics()
        
    def _load_guardrails_config(self) -> Dict[str, Any]:
        """Load guardrails configuration"""
        try:
            config_path = "./config/guardrails_config.yml"
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    return yaml.safe_load(f)
            else:
                # Create default config
                default_config = self._create_default_config()
                self._save_guardrails_config(default_config)
                return default_config
        except Exception as e:
            logger.error(f"Error loading guardrails config: {str(e)}")
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Create default guardrails configuration"""
        return {
            "enabled": True,
            "strict_mode": False,
            "max_input_length": 2000,
            "allowed_domains": [
                "conga",
                "cpq",
                "api",
                "troubleshooting",
                "authentication",
                "configuration",
                "pricing",
                "quotes"
            ],
            "blocked_categories": [
                "personal_information",
                "financial_details",
                "credentials",
                "malicious_code",
                "inappropriate_content"
            ],
            "content_filters": {
                "profanity": True,
                "personal_data": True,
                "code_injection": True,
                "prompt_injection": True
            },
            "rate_limiting": {
                "enabled": True,
                "max_requests_per_minute": 60,
                "max_requests_per_hour": 1000
            }
        }
    
    def _save_guardrails_config(self, config: Dict[str, Any]):
        """Save guardrails configuration"""
        try:
            os.makedirs("./config", exist_ok=True)
            with open("./config/guardrails_config.yml", 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
        except Exception as e:
            logger.error(f"Error saving guardrails config: {str(e)}")
    
    def _load_blocked_patterns(self) -> List[str]:
        """Load blocked input patterns"""
        return [
            # Prompt injection attempts
            r"ignore\s+previous\s+instructions",
            r"forget\s+your\s+role",
            r"act\s+as\s+if\s+you\s+are",
            r"pretend\s+to\s+be",
            r"roleplay\s+as",
            
            # Code injection attempts
            r"<script.*?>.*?</script>",
            r"javascript:",
            r"eval\s*\(",
            r"exec\s*\(",
            
            # Personal information patterns
            r"\b\d{3}-\d{2}-\d{4}\b",  # SSN pattern
            r"\b\d{4}\s*\d{4}\s*\d{4}\s*\d{4}\b",  # Credit card pattern
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email pattern
            
            # Malicious patterns
            r"DROP\s+TABLE",
            r"DELETE\s+FROM",
            r"INSERT\s+INTO",
            r"UPDATE\s+.*\s+SET",
            
            # System command attempts
            r"rm\s+-rf",
            r"sudo\s+",
            r"chmod\s+",
            r"wget\s+",
            r"curl\s+.*\|\s*sh"
        ]
    
    def _load_allowed_topics(self) -> List[str]:
        """Load list of allowed topics"""
        return [
            "conga cpq",
            "api troubleshooting",
            "authentication",
            "bearer token",
            "api endpoints",
            "error codes",
            "rate limiting",
            "pricing",
            "quotes",
            "products",
            "configuration",
            "timeout",
            "payload",
            "headers",
            "json",
            "rest api",
            "http status",
            "documentation"
        ]
    
    async def validate_input(self, user_input: str) -> bool:
        """Validate user input against guardrails"""
        try:
            if not self.config.get("enabled", True):
                return True
            
            # Check input length
            if len(user_input) > self.config.get("max_input_length", 2000):
                logger.warning("Input exceeds maximum length")
                return False
            
            # Check for blocked patterns
            if self._contains_blocked_patterns(user_input):
                logger.warning("Input contains blocked patterns")
                return False
            
            # Check content filters
            if not self._pass_content_filters(user_input):
                logger.warning("Input failed content filters")
                return False
            
            # Check topic relevance
            if self.config.get("strict_mode", False):
                if not self._is_relevant_topic(user_input):
                    logger.warning("Input is not relevant to allowed topics")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating input: {str(e)}")
            # Fail safe - block input if validation fails
            return False
    
    def _contains_blocked_patterns(self, text: str) -> bool:
        """Check if text contains any blocked patterns"""
        text_lower = text.lower()
        
        for pattern in self.blocked_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                logger.warning(f"Blocked pattern detected: {pattern}")
                return True
        
        return False
    
    def _pass_content_filters(self, text: str) -> bool:
        """Check if text passes content filters"""
        filters = self.config.get("content_filters", {})
        
        # Profanity filter
        if filters.get("profanity", True):
            if self._contains_profanity(text):
                return False
        
        # Personal data filter
        if filters.get("personal_data", True):
            if self._contains_personal_data(text):
                return False
        
        # Code injection filter
        if filters.get("code_injection", True):
            if self._contains_code_injection(text):
                return False
        
        # Prompt injection filter
        if filters.get("prompt_injection", True):
            if self._contains_prompt_injection(text):
                return False
        
        return True
    
    def _contains_profanity(self, text: str) -> bool:
        """Check for profanity (basic implementation)"""
        profanity_words = [
            "damn", "shit", "fuck", "bitch", "asshole", "bastard"
        ]
        
        text_lower = text.lower()
        for word in profanity_words:
            if word in text_lower:
                logger.warning(f"Profanity detected: {word}")
                return True
        
        return False
    
    def _contains_personal_data(self, text: str) -> bool:
        """Check for personal data patterns"""
        # SSN pattern
        if re.search(r'\b\d{3}-\d{2}-\d{4}\b', text):
            logger.warning("SSN pattern detected")
            return True
        
        # Credit card pattern
        if re.search(r'\b\d{4}\s*\d{4}\s*\d{4}\s*\d{4}\b', text):
            logger.warning("Credit card pattern detected")
            return True
        
        # Phone number pattern
        if re.search(r'\b\d{3}-\d{3}-\d{4}\b', text):
            logger.warning("Phone number pattern detected")
            return True
        
        return False
    
    def _contains_code_injection(self, text: str) -> bool:
        """Check for code injection attempts"""
        injection_patterns = [
            r"<script.*?>.*?</script>",
            r"javascript:",
            r"eval\s*\(",
            r"exec\s*\(",
            r"system\s*\(",
            r"shell_exec\s*\(",
            r"passthru\s*\(",
            r"DROP\s+TABLE",
            r"DELETE\s+FROM",
            r"INSERT\s+INTO",
            r"UPDATE\s+.*\s+SET"
        ]
        
        for pattern in injection_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                logger.warning(f"Code injection pattern detected: {pattern}")
                return True
        
        return False
    
    def _contains_prompt_injection(self, text: str) -> bool:
        """Check for prompt injection attempts"""
        injection_patterns = [
            r"ignore\s+previous\s+instructions",
            r"forget\s+your\s+role",
            r"act\s+as\s+if\s+you\s+are",
            r"pretend\s+to\s+be",
            r"roleplay\s+as",
            r"you\s+are\s+now",
            r"from\s+now\s+on",
            r"new\s+instructions",
            r"system\s+prompt",
            r"assistant\s+mode"
        ]
        
        for pattern in injection_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                logger.warning(f"Prompt injection pattern detected: {pattern}")
                return True
        
        return False
    
    def _is_relevant_topic(self, text: str) -> bool:
        """Check if text is relevant to allowed topics"""
        text_lower = text.lower()
        
        # Check if any allowed topic keywords are present
        for topic in self.allowed_topics:
            topic_words = topic.lower().split()
            if all(word in text_lower for word in topic_words):
                return True
        
        # Check for general technical keywords
        technical_keywords = [
            "api", "endpoint", "error", "code", "status", "response",
            "request", "header", "payload", "json", "authentication",
            "authorization", "token", "troubleshoot", "debug", "fix",
            "issue", "problem", "help", "how", "what", "why", "when"
        ]
        
        keyword_count = sum(1 for keyword in technical_keywords if keyword in text_lower)
        return keyword_count >= 2  # At least 2 technical keywords
    
    async def get_violation_reason(self, user_input: str) -> Optional[str]:
        """Get detailed reason for input violation"""
        try:
            # Check input length
            if len(user_input) > self.config.get("max_input_length", 2000):
                return f"Input exceeds maximum length of {self.config.get('max_input_length', 2000)} characters"
            
            # Check for blocked patterns
            for pattern in self.blocked_patterns:
                if re.search(pattern, user_input.lower(), re.IGNORECASE):
                    return f"Input contains blocked pattern: {pattern}"
            
            # Check content filters
            filters = self.config.get("content_filters", {})
            
            if filters.get("profanity", True) and self._contains_profanity(user_input):
                return "Input contains inappropriate language"
            
            if filters.get("personal_data", True) and self._contains_personal_data(user_input):
                return "Input contains personal data that should not be shared"
            
            if filters.get("code_injection", True) and self._contains_code_injection(user_input):
                return "Input contains potential code injection attempts"
            
            if filters.get("prompt_injection", True) and self._contains_prompt_injection(user_input):
                return "Input contains prompt injection attempts"
            
            # Check topic relevance in strict mode
            if self.config.get("strict_mode", False) and not self._is_relevant_topic(user_input):
                return "Input is not relevant to Conga CPQ troubleshooting topics"
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting violation reason: {str(e)}")
            return "Unable to process input due to technical error"
    
    async def sanitize_input(self, user_input: str) -> str:
        """Sanitize user input by removing problematic content"""
        try:
            sanitized = user_input
            
            # Remove HTML tags
            sanitized = re.sub(r'<[^>]+>', '', sanitized)
            
            # Remove JavaScript
            sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)
            
            # Remove SQL injection attempts
            sql_patterns = [
                r"DROP\s+TABLE",
                r"DELETE\s+FROM",
                r"INSERT\s+INTO",
                r"UPDATE\s+.*\s+SET"
            ]
            
            for pattern in sql_patterns:
                sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
            
            # Remove excessive whitespace
            sanitized = re.sub(r'\s+', ' ', sanitized).strip()
            
            # Truncate if too long
            max_length = self.config.get("max_input_length", 2000)
            if len(sanitized) > max_length:
                sanitized = sanitized[:max_length] + "..."
            
            return sanitized
            
        except Exception as e:
            logger.error(f"Error sanitizing input: {str(e)}")
            return user_input  # Return original if sanitization fails
    
    async def get_guardrails_status(self) -> Dict[str, Any]:
        """Get current guardrails configuration and status"""
        return {
            "enabled": self.config.get("enabled", True),
            "strict_mode": self.config.get("strict_mode", False),
            "max_input_length": self.config.get("max_input_length", 2000),
            "content_filters": self.config.get("content_filters", {}),
            "allowed_domains_count": len(self.config.get("allowed_domains", [])),
            "blocked_patterns_count": len(self.blocked_patterns),
            "allowed_topics_count": len(self.allowed_topics)
        }
    
    async def update_config(self, new_config: Dict[str, Any]) -> bool:
        """Update guardrails configuration"""
        try:
            # Validate new config
            required_keys = ["enabled", "max_input_length", "content_filters"]
            for key in required_keys:
                if key not in new_config:
                    logger.error(f"Missing required config key: {key}")
                    return False
            
            # Update config
            self.config.update(new_config)
            self._save_guardrails_config(self.config)
            
            logger.info("Guardrails configuration updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error updating guardrails config: {str(e)}")
            return False