import os
import pickle
import logging
from typing import List, Dict, Optional, Tuple
import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document
from utils.config import settings
from data.embeddings import MedicalEmbeddings

logger = logging.getLogger(__name__)

class MedicalVectorStore:
    def __init__(self):
        self.store_path = settings.VECTOR_STORE_PATH
        self.embeddings = MedicalEmbeddings()
        self.vector_store = None
        self.documents = []
        
    async def initialize(self):
        """Initialize vector store and embeddings"""
        await self.embeddings.initialize()
        
        # Create directory if it doesn't exist
        os.makedirs(self.store_path, exist_ok=True)
        
        # Initialize Chroma vector store
        embedding_function = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL,
            model_kwargs={'device': 'cuda' if torch.cuda.is_available() else 'cpu'}
        )
        
        self.vector_store = Chroma(
            persist_directory=self.store_path,
            embedding_function=embedding_function,
            collection_name="medical_qa"
        )
        
        logger.info("Vector store initialized successfully")
    
    async def add_documents(self, documents: List[Dict]) -> None:
        """Add documents to vector store"""
        try:
            # Convert to LangChain Document format
            langchain_docs = []
            for doc in documents:
                content = f"Question: {doc['question']}\nAnswer: {doc['answer']}"
                metadata = {
                    'id': doc.get('id', ''),
                    'subject': doc.get('subject', ''),
                    'topic': doc.get('topic', ''),
                    'question': doc['question'],
                    'answer': doc['answer']
                }
                langchain_docs.append(Document(page_content=content, metadata=metadata))
            
            # Add to vector store
            self.vector_store.add_documents(langchain_docs)
            self.documents.extend(documents)
            
            logger.info(f"Added {len(documents)} documents to vector store")
            
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}")
            raise
    
    async def similarity_search(self, query: str, k: int = 5, 
                              filter_dict: Optional[Dict] = None) -> List[Document]:
        """Search for similar documents"""
        try:
            if filter_dict:
                results = self.vector_store.similarity_search(
                    query, k=k, filter=filter_dict
                )
            else:
                results = self.vector_store.similarity_search(query, k=k)
            
            logger.info(f"Found {len(results)} similar documents for query")
            return results
            
        except Exception as e:
            logger.error(f"Error in similarity search: {e}")
            raise
    
    async def similarity_search_with_score(self, query: str, k: int = 5) -> List[Tuple[Document, float]]:
        """Search for similar documents with similarity scores"""
        try:
            results = self.vector_store.similarity_search_with_score(query, k=k)
            logger.info(f"Found {len(results)} similar documents with scores")
            return results
        except Exception as e:
            logger.error(f"Error in similarity search with score: {e}")
            raise
    
    def persist(self):
        """Persist vector store to disk"""
        try:
            self.vector_store.persist()
            logger.info("Vector store persisted successfully")
        except Exception as e:
            logger.error(f"Error persisting vector store: {e}")
            raise
    
    def get_collection_count(self) -> int:
        """Get number of documents in collection"""
        try:
            return self.vector_store._collection.count()
        except Exception as e:
            logger.error(f"Error getting collection count: {e}")
            return 0