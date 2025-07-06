"""
Chat service for handling RAG queries and conversation management
"""

import json
import logging
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from openai import AzureOpenAI
from config.settings import settings
from models.chat_models import ChatResponse, ChatMessage, APICallInfo, Conversation
from services.document_service import DocumentService

logger = logging.getLogger(__name__)


class ChatService:
    """Service for chat functionality with RAG"""
    
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            azure_endpoint=settings.azure_openai_endpoint
        )
        
        self.document_service = DocumentService()
        self.conversations: Dict[str, Conversation] = {}
        
        # Few-shot examples for better responses
        self.few_shot_examples = self._load_few_shot_examples()
    
    def _load_few_shot_examples(self) -> List[Dict[str, str]]:
        """Load few-shot examples for prompting"""
        return [
            {
                "user": "How do I fix 401 authentication errors?",
                "assistant": "For 401 authentication errors, check these steps:\n1. Verify your bearer token is not expired\n2. Ensure the token format is correct: 'Bearer <token>'\n3. Check that the token has required scopes\n4. If issues persist, regenerate your token\n\nWould you like me to help you test your current bearer token?"
            },
            {
                "user": "What's the payload for creating a quote?",
                "assistant": "To create a quote using the Quote Management API, use this payload structure:\n\n```json\n{\n  \"accountId\": \"string\",\n  \"opportunityId\": \"string\",\n  \"products\": [\n    {\n      \"productId\": \"string\",\n      \"quantity\": \"number\",\n      \"listPrice\": \"number\"\n    }\n  ]\n}\n```\n\nThe endpoint is `POST /api/v1/quotes` with Authorization header. Do you have a bearer token to test this API?"
            },
            {
                "user": "How to handle rate limiting?",
                "assistant": "For 429 Rate Limit Exceeded errors:\n1. Implement exponential backoff in your retry logic\n2. Reduce request frequency\n3. Consider caching responses to reduce API calls\n4. Contact support if you need higher rate limits\n\nWould you like help implementing a retry mechanism?"
            }
        ]
    
    async def process_query(
        self, 
        query: str, 
        conversation_id: Optional[str] = None,
        bearer_token: Optional[str] = None
    ) -> ChatResponse:
        """Process user query with RAG"""
        try:
            # Generate conversation ID if not provided
            if not conversation_id:
                conversation_id = str(uuid.uuid4())
            
            # Search for relevant context
            context_results = await self.document_service.search_documents(query)
            
            # Check if query is out of context
            if not context_results:
                return ChatResponse(
                    response="Sorry!! The query is out of my context or knowledge base. Please ask questions related to Conga CPQ Turbo API troubleshooting.",
                    context_used=False,
                    confidence_score=0.0,
                    requires_api_execution=False,
                    conversation_id=conversation_id
                )
            
            # Build context from search results
            context = self._build_context(context_results)
            
            # Get conversation history
            conversation_history = self._get_conversation_history(conversation_id)
            
            # Generate response using Azure OpenAI
            response_data = await self._generate_response(
                query=query,
                context=context,
                conversation_history=conversation_history,
                bearer_token=bearer_token
            )
            
            # Store conversation
            self._store_conversation_message(conversation_id, "user", query)
            self._store_conversation_message(
                conversation_id, 
                "assistant", 
                response_data["response"],
                context_used=True,
                confidence_score=response_data["confidence_score"]
            )
            
            return ChatResponse(
                response=response_data["response"],
                context_used=True,
                confidence_score=response_data["confidence_score"],
                requires_api_execution=response_data.get("requires_api_execution", False),
                api_info=response_data.get("api_info"),
                suggested_follow_ups=response_data.get("suggested_follow_ups"),
                conversation_id=conversation_id
            )
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            raise
    
    def _build_context(self, context_results: List[Dict[str, Any]]) -> str:
        """Build context string from search results"""
        context_parts = []
        for result in context_results:
            context_parts.append(f"[Source: {result['metadata']['filename']}]")
            context_parts.append(result['content'])
            context_parts.append("")  # Empty line for separation
        
        return "\n".join(context_parts)
    
    async def _generate_response(
        self,
        query: str,
        context: str,
        conversation_history: List[ChatMessage],
        bearer_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate response using Azure OpenAI"""
        
        # Build system prompt with few-shot examples
        system_prompt = self._build_system_prompt()
        
        # Build user prompt with context
        user_prompt = self._build_user_prompt(query, context, bearer_token)
        
        # Prepare messages for OpenAI
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add few-shot examples
        for example in self.few_shot_examples:
            messages.append({"role": "user", "content": example["user"]})
            messages.append({"role": "assistant", "content": example["assistant"]})
        
        # Add conversation history
        for msg in conversation_history[-6:]:  # Last 6 messages for context
            messages.append({"role": msg.role, "content": msg.content})
        
        # Add current query
        messages.append({"role": "user", "content": user_prompt})
        
        try:
            response = self.client.chat.completions.create(
                model=settings.azure_openai_deployment_name,
                messages=messages,
                temperature=settings.temperature,
                max_tokens=settings.max_tokens
            )
            
            response_text = response.choices[0].message.content
            
            # Parse response for API execution requirements
            api_info = self._extract_api_info(response_text)
            requires_api_execution = api_info is not None and bearer_token is not None
            
            # Generate suggested follow-ups
            suggested_follow_ups = self._generate_follow_ups(query, response_text)
            
            # Calculate confidence score based on context relevance
            confidence_score = self._calculate_confidence_score(context, response_text)
            
            return {
                "response": response_text,
                "confidence_score": confidence_score,
                "requires_api_execution": requires_api_execution,
                "api_info": api_info,
                "suggested_follow_ups": suggested_follow_ups
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for the assistant"""
        return """You are a specialized troubleshooting assistant for Conga CPQ Turbo API. Your role is to:

1. Help users troubleshoot API issues using the provided documentation
2. Provide clear, actionable solutions
3. When mentioning specific API endpoints, include all necessary details (method, headers, payload schema)
4. If a user asks about API execution and the response contains API information, ask for their bearer token
5. Stay within the context of the provided documentation
6. If a question is outside your knowledge base, clearly state that

Guidelines:
- Be concise but thorough
- Use bullet points for step-by-step instructions
- Include code examples when relevant
- Always mention security best practices
- If API execution is possible, format the response to indicate this clearly

Remember: Only answer questions related to Conga CPQ Turbo API troubleshooting and documentation."""
    
    def _build_user_prompt(self, query: str, context: str, bearer_token: Optional[str]) -> str:
        """Build user prompt with context"""
        prompt = f"Context from documentation:\n{context}\n\n"
        prompt += f"User Question: {query}\n\n"
        
        if bearer_token:
            prompt += "Note: User has provided a bearer token for API execution.\n\n"
        
        prompt += "Please provide a helpful response based on the context provided."
        
        return prompt
    
    def _extract_api_info(self, response_text: str) -> Optional[APICallInfo]:
        """Extract API information from response if present"""
        # Look for API endpoint patterns
        endpoint_pattern = r'`(GET|POST|PUT|DELETE|PATCH)\s+([^`]+)`'
        endpoint_match = re.search(endpoint_pattern, response_text)
        
        if endpoint_match:
            method = endpoint_match.group(1)
            endpoint = endpoint_match.group(2).strip()
            
            # Extract description from surrounding text
            description = "API endpoint mentioned in troubleshooting response"
            
            return APICallInfo(
                endpoint=endpoint,
                method=method,
                headers={"Authorization": "Bearer <token>", "Content-Type": "application/json"},
                description=description
            )
        
        return None
    
    def _generate_follow_ups(self, query: str, response: str) -> List[str]:
        """Generate suggested follow-up questions"""
        follow_ups = []
        
        # Common follow-ups based on query content
        if "authentication" in query.lower() or "401" in query:
            follow_ups.extend([
                "How do I refresh my bearer token?",
                "What are the required scopes for API access?"
            ])
        
        if "api" in query.lower() and "endpoint" in response.lower():
            follow_ups.extend([
                "Can you show me a complete example request?",
                "What are the common error responses for this API?"
            ])
        
        if "error" in query.lower():
            follow_ups.extend([
                "How can I debug this issue further?",
                "Are there any logs I should check?"
            ])
        
        return follow_ups[:3]  # Limit to 3 suggestions
    
    def _calculate_confidence_score(self, context: str, response: str) -> float:
        """Calculate confidence score based on context relevance"""
        if not context or not response:
            return 0.5
        
        # Simple scoring based on keyword overlap
        context_words = set(context.lower().split())
        response_words = set(response.lower().split())
        
        # Calculate overlap
        common_words = context_words.intersection(response_words)
        
        if not context_words:
            return 0.5
        
        overlap_ratio = len(common_words) / len(context_words)
        
        # Boost score if response contains structured information
        if any(keyword in response.lower() for keyword in ["endpoint", "headers", "payload", "solution"]):
            overlap_ratio += 0.2
        
        return min(overlap_ratio, 1.0)
    
    def _get_conversation_history(self, conversation_id: str) -> List[ChatMessage]:
        """Get conversation history"""
        if conversation_id in self.conversations:
            return self.conversations[conversation_id].messages
        return []
    
    def _store_conversation_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        context_used: bool = False,
        confidence_score: Optional[float] = None
    ):
        """Store conversation message"""
        message = ChatMessage(
            role=role,
            content=content,
            context_used=context_used,
            confidence_score=confidence_score
        )
        
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = Conversation(
                conversation_id=conversation_id,
                messages=[],
                created_at=datetime.utcnow(),
                last_updated=datetime.utcnow()
            )
        
        self.conversations[conversation_id].messages.append(message)
        self.conversations[conversation_id].last_updated = datetime.utcnow()
    
    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get conversation by ID"""
        return self.conversations.get(conversation_id)
    
    async def delete_conversation(self, conversation_id: str) -> bool:
        """Delete conversation"""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            return True
        return False