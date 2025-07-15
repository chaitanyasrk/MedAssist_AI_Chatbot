import torch
import torch.nn.functional as F
from sentence_transformers import SentenceTransformer
from typing import List, Optional
import numpy as np
import logging
from utils.config import settings

logger = logging.getLogger(__name__)

class MedicalEmbeddings:
    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or settings.EMBEDDING_MODEL
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        
    async def initialize(self):
        """Initialize the embedding model"""
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name, device=str(self.device))
            logger.info(f"Embedding model loaded on device: {self.device}")
        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            raise
    
    def encode_texts(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """Encode texts to embeddings"""
        if not self.model:
            raise ValueError("Model not initialized. Call initialize() first.")
        
        try:
            with torch.no_grad():
                embeddings = self.model.encode(
                    texts,
                    batch_size=batch_size,
                    convert_to_tensor=True,
                    device=self.device
                )
                return embeddings.cpu().numpy()
        except Exception as e:
            logger.error(f"Error encoding texts: {e}")
            raise
    
    def encode_single_text(self, text: str) -> np.ndarray:
        """Encode single text to embedding"""
        return self.encode_texts([text])[0]
    
    def compute_similarity(self, query_embedding: np.ndarray, 
                          candidate_embeddings: np.ndarray) -> np.ndarray:
        """Compute cosine similarity between query and candidates"""
        try:
            # Convert to tensors
            query_tensor = torch.tensor(query_embedding, dtype=torch.float32)
            candidate_tensor = torch.tensor(candidate_embeddings, dtype=torch.float32)
            
            # Normalize vectors
            query_norm = F.normalize(query_tensor.unsqueeze(0), p=2, dim=1)
            candidate_norm = F.normalize(candidate_tensor, p=2, dim=1)
            
            # Compute cosine similarity
            similarities = torch.mm(query_norm, candidate_norm.transpose(0, 1))
            
            return similarities.squeeze().numpy()
        except Exception as e:
            logger.error(f"Error computing similarity: {e}")
            raise
    
    def get_top_k_similar(self, query_embedding: np.ndarray,
                         candidate_embeddings: np.ndarray,
                         k: int = 5) -> List[int]:
        """Get indices of top-k most similar candidates"""
        similarities = self.compute_similarity(query_embedding, candidate_embeddings)
        top_k_indices = np.argsort(similarities)[-k:][::-1]
        return top_k_indices.tolist()