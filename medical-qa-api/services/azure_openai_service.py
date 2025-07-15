import asyncio
import logging
from typing import List, Dict, Optional, Any
from openai import AsyncAzureOpenAI
from langchain.llms import AzureOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import AzureChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from utils.config import settings

logger = logging.getLogger(__name__)

class AzureOpenAIService:
    def __init__(self):
        self.client = None
        self.chat_model = None
        self.embeddings_model = None
        
    async def initialize(self):
        """Initialize Azure OpenAI service"""
        try:
            # Initialize async client
            self.client = AsyncAzureOpenAI(
                api_key=settings.AZURE_OPENAI_API_KEY,
                api_version=settings.AZURE_OPENAI_API_VERSION,
                azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
            )
            
            # Initialize LangChain models
            self.chat_model = AzureChatOpenAI(
                deployment_name=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
                model_name="gpt-4",
                azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
                api_key=settings.AZURE_OPENAI_API_KEY,
                api_version=settings.AZURE_OPENAI_API_VERSION,
                temperature=0.1,
                max_tokens=1000
            )
            
            self.embeddings_model = OpenAIEmbeddings(
                deployment=settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
                model="text-embedding-ada-002",
                azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
                api_key=settings.AZURE_OPENAI_API_KEY,
                api_version=settings.AZURE_OPENAI_API_VERSION
            )
            
            logger.info("Azure OpenAI service initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing Azure OpenAI service: {e}")
            raise
    
    async def generate_response(self, messages: List[Dict[str, str]], 
                              temperature: float = 0.1, 
                              max_tokens: int = 1000) -> str:
        """Generate response using Azure OpenAI"""
        try:
            response = await self.client.chat.completions.create(
                model=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=0.95,
                frequency_penalty=0,
                presence_penalty=0
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise
    
    def create_medical_prompt(self, query: str, context_documents: List[Dict]) -> List[Dict[str, str]]:
        """Create medical-specific prompt with context"""
        system_prompt = """You are a medical knowledge assistant providing accurate, evidence-based information about medicine and healthcare. 

Guidelines:
1. Provide accurate medical information based on established medical knowledge
2. Always clarify that your responses are for educational purposes only
3. Recommend consulting healthcare professionals for personal medical concerns
4. Use the provided context documents to support your answers
5. If you're unsure about something, acknowledge the uncertainty
6. Focus on peer-reviewed medical knowledge and established clinical guidelines

IMPORTANT: Do not provide personal medical advice or diagnosis. Always recommend consulting with qualified healthcare professionals for personal medical concerns.
"""
        
        # Build context from retrieved documents
        context = "\n\n".join([
            f"Context {i+1}:\nQuestion: {doc['question']}\nAnswer: {doc['answer']}"
            for i, doc in enumerate(context_documents[:3])
        ])
        
        user_prompt = f"""Based on the following medical knowledge context, please answer the question:

CONTEXT:
{context}

QUESTION: {query}

Please provide a comprehensive, accurate answer based on the context and established medical knowledge. If the context doesn't fully address the question, use your medical knowledge while noting any limitations."""

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for texts using Azure OpenAI"""
        try:
            response = await self.client.embeddings.create(
                model=settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
                input=texts
            )
            return [embedding.embedding for embedding in response.data]
        except Exception as e:
            logger.error(f"Error getting embeddings: {e}")
            raise