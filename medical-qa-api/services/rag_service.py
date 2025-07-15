"""
Complete RAG Service with Azure OpenAI and Medical Dataset Integration
"""

import asyncio
import logging
from typing import List, Dict, Optional, Tuple
from openai import AsyncAzureOpenAI
from utils.config import settings
from services.medical_validator import MedicalValidator, MedicalQueryType

logger = logging.getLogger(__name__)

class MedicalRAGService:
    def __init__(self):
        self.azure_client = None
        self.medical_validator = MedicalValidator()
        self.is_initialized = False
        
        # Mock medical knowledge base for demonstration
        # In production, this would be loaded from the actual dataset
        self.medical_knowledge = [
            {
                "question": "What is diabetes?",
                "answer": "Diabetes is a group of metabolic disorders characterized by high blood sugar levels over a prolonged period. There are mainly two types: Type 1 diabetes results from the pancreas's failure to produce enough insulin, while Type 2 diabetes begins with insulin resistance.",
                "category": "endocrinology"
            },
            {
                "question": "What are the symptoms of hypertension?",
                "answer": "Hypertension, or high blood pressure, is often called a 'silent killer' because it typically has no symptoms. However, in severe cases, symptoms may include headaches, shortness of breath, dizziness, chest pain, heart palpitations, and nosebleeds.",
                "category": "cardiology"
            },
            {
                "question": "What causes heart disease?",
                "answer": "Heart disease can be caused by various factors including high blood pressure, high cholesterol, diabetes, smoking, obesity, physical inactivity, unhealthy diet, excessive alcohol consumption, stress, and genetic factors. Age and family history also play important roles.",
                "category": "cardiology"
            },
            {
                "question": "How do vaccines work?",
                "answer": "Vaccines work by training the immune system to recognize and combat pathogens. They contain antigens that resemble disease-causing microorganisms, which stimulate the immune system to produce antibodies and activate immune cells without causing the actual disease.",
                "category": "immunology"
            },
            {
                "question": "What is the difference between virus and bacteria?",
                "answer": "Viruses are much smaller than bacteria and require a living host to reproduce, while bacteria are single-celled organisms that can reproduce independently. Antibiotics work against bacteria but not viruses. Viral infections often resolve on their own, while bacterial infections may require antibiotic treatment.",
                "category": "microbiology"
            }
        ]
        
    async def initialize(self):
        """Initialize the RAG service"""
        try:
            logger.info("Initializing Medical RAG Service...")
            
            # Check if Azure OpenAI is configured
            if not settings.has_azure_openai_config():
                logger.warning("Azure OpenAI not configured - using mock responses")
                self.azure_client = None
            else:
                # Initialize Azure OpenAI client
                self.azure_client = AsyncAzureOpenAI(
                    api_key=settings.AZURE_OPENAI_API_KEY,
                    api_version=settings.AZURE_OPENAI_API_VERSION,
                    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
                )
                logger.info("Azure OpenAI client initialized")
            
            self.is_initialized = True
            logger.info("✅ Medical RAG Service initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Error initializing RAG service: {e}")
            # Set to basic mode if initialization fails
            self.azure_client = None
            self.is_initialized = True
            logger.warning("RAG service running in basic mode")
    
    async def process_query(self, query: str, session_id: str) -> Dict:
        """Process medical query using RAG"""
        if not self.is_initialized:
            raise ValueError("RAG service not initialized")
        
        try:
            # Step 1: Validate if query is medical
            is_medical, query_type, confidence = self.medical_validator.validate_medical_query(query)
            
            if not is_medical:
                return {
                    "response": self.medical_validator.get_rejection_message(query_type),
                    "is_medical": False,
                    "confidence": confidence,
                    "retrieved_context": [],
                    "evaluation_ready": False,
                    "query_type": query_type.value if hasattr(query_type, 'value') else str(query_type)
                }
            
            # Step 2: Check if query is safe (no personal medical advice)
            is_safe, safety_message = self.medical_validator.is_safe_medical_query(query)
            if not is_safe:
                return {
                    "response": safety_message,
                    "is_medical": True,
                    "confidence": confidence,
                    "retrieved_context": [],
                    "evaluation_ready": False,
                    "query_type": query_type.value if hasattr(query_type, 'value') else str(query_type)
                }
            
            # Step 3: Retrieve relevant context
            context_docs = self._retrieve_relevant_context(query, k=3)
            
            # Step 4: Generate response
            if self.azure_client:
                response = await self._generate_azure_response(query, context_docs)
            else:
                response = self._generate_mock_response(query, context_docs)
            
            return {
                "response": response,
                "is_medical": True,
                "query_type": query_type.value if hasattr(query_type, 'value') else str(query_type),
                "confidence": confidence,
                "retrieved_context": context_docs,
                "evaluation_ready": True
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            # Return a safe fallback response
            return {
                "response": "I apologize, but I'm experiencing technical difficulties. Please try again later or consult with a healthcare professional for medical information.",
                "is_medical": True,
                "confidence": 0.5,
                "retrieved_context": [],
                "evaluation_ready": False,
                "query_type": "general"
            }
    
    def _retrieve_relevant_context(self, query: str, k: int = 3) -> List[Dict]:
        """Retrieve relevant context from medical knowledge base"""
        # Simple keyword-based retrieval for demonstration
        # In production, this would use proper vector similarity search
        
        query_lower = query.lower()
        relevant_docs = []
        
        for doc in self.medical_knowledge:
            # Calculate simple relevance score based on keyword overlap
            question_words = set(doc["question"].lower().split())
            query_words = set(query_lower.split())
            
            # Calculate Jaccard similarity
            intersection = len(question_words.intersection(query_words))
            union = len(question_words.union(query_words))
            similarity = intersection / union if union > 0 else 0
            
            # Also check if query words appear in the answer
            answer_words = set(doc["answer"].lower().split())
            answer_intersection = len(answer_words.intersection(query_words))
            answer_similarity = answer_intersection / len(query_words) if len(query_words) > 0 else 0
            
            # Combined similarity score
            combined_similarity = (similarity + answer_similarity) / 2
            
            if combined_similarity > 0.1:  # Threshold for relevance
                relevant_docs.append({
                    "question": doc["question"],
                    "answer": doc["answer"],
                    "category": doc["category"],
                    "similarity_score": combined_similarity
                })
        
        # Sort by similarity and return top k
        relevant_docs.sort(key=lambda x: x["similarity_score"], reverse=True)
        return relevant_docs[:k]
    
    async def _generate_azure_response(self, query: str, context_docs: List[Dict]) -> str:
        """Generate response using Azure OpenAI"""
        try:
            # Build context from retrieved documents
            context = "\n\n".join([
                f"Context {i+1}:\nQuestion: {doc['question']}\nAnswer: {doc['answer']}"
                for i, doc in enumerate(context_docs[:3])
            ])
            
            system_prompt = """You are a medical knowledge assistant providing accurate, evidence-based information about medicine and healthcare. 

Guidelines:
1. Provide accurate medical information based on established medical knowledge
2. Always clarify that your responses are for educational purposes only
3. Recommend consulting healthcare professionals for personal medical concerns
4. Use the provided context documents to support your answers
5. If you're unsure about something, acknowledge the uncertainty
6. Focus on peer-reviewed medical knowledge and established clinical guidelines

IMPORTANT: Do not provide personal medical advice or diagnosis. Always recommend consulting with qualified healthcare professionals for personal medical concerns."""

            user_prompt = f"""Based on the following medical knowledge context, please answer the question:

CONTEXT:
{context}

QUESTION: {query}

Please provide a comprehensive, accurate answer based on the context and established medical knowledge. If the context doesn't fully address the question, use your medical knowledge while noting any limitations."""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            response = await self.azure_client.chat.completions.create(
                model=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
                messages=messages,
                temperature=0.1,
                max_tokens=1000,
                top_p=0.95
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating Azure response: {e}")
            return self._generate_mock_response(query, context_docs)
    
    def _generate_mock_response(self, query: str, context_docs: List[Dict]) -> str:
        """Generate mock response when Azure OpenAI is not available"""
        if context_docs:
            # Use the most relevant context document
            best_context = context_docs[0]
            response = f"""Based on medical knowledge about {best_context['question'].lower()}: 

{best_context['answer']}

This information is provided for educational purposes and is based on established medical knowledge. However, I'm currently running with limited AI capabilities. For more detailed and personalized information, please consult with qualified healthcare professionals."""
        else:
            # Generic medical response
            response = f"""Thank you for your medical question about "{query}". 

While I don't have specific information readily available about this topic in my current knowledge base, I recommend consulting with qualified healthcare professionals who can provide accurate, personalized medical information based on current medical guidelines and research.

For reliable medical information, you can also refer to established medical resources such as medical institutions, peer-reviewed medical literature, or certified healthcare websites."""
        
        return response
    
    async def get_evaluation_dataset(self) -> List[Dict]:
        """Get evaluation dataset for testing"""
        # Return a subset of the knowledge base for evaluation
        return self.medical_knowledge[-2:]  # Last 2 items for evaluation
    
    def get_available_categories(self) -> List[str]:
        """Get available medical categories"""
        return list(set(doc["category"] for doc in self.medical_knowledge))


class MedicalValidator:
    """Medical query validator"""
    
    def __init__(self):
        self.medical_keywords = [
            "medical", "medicine", "health", "disease", "condition", "symptoms", "treatment",
            "diagnosis", "medication", "therapy", "doctor", "hospital", "clinic", "patient",
            "diabetes", "hypertension", "heart", "blood", "pressure", "cholesterol", "cancer",
            "virus", "bacteria", "infection", "fever", "pain", "headache", "nausea", "fatigue"
        ]
        
        self.non_medical_keywords = [
            "weather", "sports", "politics", "cooking", "travel", "entertainment",
            "technology", "programming", "business", "finance", "music", "art"
        ]
    
    def validate_medical_query(self, query: str) -> Tuple[bool, MedicalQueryType, float]:
        """Validate if query is medical-related"""
        query_lower = query.lower()
        
        # Check for non-medical keywords
        non_medical_score = sum(1 for keyword in self.non_medical_keywords if keyword in query_lower)
        if non_medical_score > 0:
            return False, MedicalQueryType.INVALID, 0.1
        
        # Check for medical keywords
        medical_score = sum(1 for keyword in self.medical_keywords if keyword in query_lower)
        
        if medical_score > 0:
            confidence = min(medical_score / 3.0, 1.0)  # Normalize confidence
            return True, MedicalQueryType.GENERAL, confidence
        
        return False, MedicalQueryType.INVALID, 0.0
    
    def is_safe_medical_query(self, query: str) -> Tuple[bool, Optional[str]]:
        """Check if medical query is safe (no personal medical advice)"""
        query_lower = query.lower()
        
        unsafe_patterns = [
            "should i", "what should i", "i have", "i am experiencing", "i feel",
            "diagnose me", "what do i have", "am i", "my symptoms", "i think i have"
        ]
        
        for pattern in unsafe_patterns:
            if pattern in query_lower:
                return False, "I cannot provide personal medical advice. Please consult with a healthcare professional for personal medical concerns."
        
        return True, None
    
    def get_rejection_message(self, query_type) -> str:
        """Get appropriate rejection message"""
        return "I'm sorry, but I can only answer medical and healthcare-related questions. Please ask about medical conditions, treatments, medications, anatomy, or physiology."


# Enum for query types
class MedicalQueryType:
    GENERAL = "general"
    DIAGNOSIS = "diagnosis"
    TREATMENT = "treatment"
    MEDICATION = "medication"
    INVALID = "invalid"