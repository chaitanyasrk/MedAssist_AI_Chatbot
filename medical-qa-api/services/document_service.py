"""
Document processing service using ChromaDB with SentenceTransformer embeddings
Following the approach from the Jupyter notebook
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
import hashlib
from datetime import datetime

import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer

from config.settings import settings

logger = logging.getLogger(__name__)


class DocumentService:
    """Service for document processing and vector storage using local embeddings"""
    
    def __init__(self):
        # Initialize SentenceTransformer for embeddings (similar to the notebook)
        # Using the same model as in the notebook: 'thenlper/gte-large'
        logger.info("Loading SentenceTransformer model: thenlper/gte-large")
        self.embedding_model = SentenceTransformer('thenlper/gte-large')
        
        # Initialize ChromaDB
        os.makedirs(settings.vector_db_path, exist_ok=True)
        self.chroma_client = chromadb.PersistentClient(
            path=settings.vector_db_path,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        self.collection = self.chroma_client.get_or_create_collection(
            name=settings.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        logger.info(f"ChromaDB initialized at: {settings.vector_db_path}")
        
    def create_embedding(self, text: str) -> List[float]:
        """Create embedding for text using SentenceTransformer"""
        try:
            # Use SentenceTransformer to encode the text
            embedding = self.embedding_model.encode(text)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error creating embedding: {str(e)}")
            raise
    
    def chunk_document(self, content: str, chunk_size: int = 512, overlap: int = 16) -> List[str]:
        """
        Split document into overlapping chunks
        Using similar parameters as in the notebook: chunk_size=512, overlap=16
        """
        chunks = []
        start = 0
        
        while start < len(content):
            end = start + chunk_size
            chunk = content[start:end]
            
            # Try to break at word boundary
            if end < len(content):
                last_space = chunk.rfind(' ')
                if last_space > chunk_size // 2:
                    chunk = chunk[:last_space]
                    end = start + last_space
            
            chunks.append(chunk.strip())
            start = end - overlap
            
            if start >= len(content):
                break
                
        return [chunk for chunk in chunks if chunk]
    
    async def process_document(
        self, 
        content: str, 
        filename: str, 
        document_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Process document and store in ChromaDB"""
        try:
            # Generate document ID
            doc_id = hashlib.md5(f"{filename}_{content[:100]}".encode()).hexdigest()
            
            # Chunk the document using the same approach as the notebook
            chunks = self.chunk_document(content)
            logger.info(f"Split document {filename} into {len(chunks)} chunks")
            
            # Create embeddings and store
            chunk_ids = []
            embeddings = []
            documents = []
            metadatas = []
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"{doc_id}_chunk_{i}"
                embedding = self.create_embedding(chunk)
                
                chunk_metadata = {
                    "document_id": doc_id,
                    "filename": filename,
                    "document_type": document_type,
                    "chunk_index": i,
                    "chunk_count": len(chunks),
                    "created_at": datetime.utcnow().isoformat(),
                    **(metadata or {})
                }
                
                chunk_ids.append(chunk_id)
                embeddings.append(embedding)
                documents.append(chunk)
                metadatas.append(chunk_metadata)
            
            # Store in ChromaDB (similar to the notebook's approach)
            self.collection.add(
                ids=chunk_ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )
            
            logger.info(f"Successfully processed document {filename} with ID {doc_id}")
            return doc_id
            
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            raise
    
    async def search_documents(
        self, 
        query: str, 
        n_results: int = None,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search documents using semantic similarity (following notebook approach)"""
        try:
            n_results = n_results or settings.top_k_results
            
            # Create query embedding using SentenceTransformer
            query_embedding = self.create_embedding(query)
            
            # Search in ChromaDB (similar to notebook's retriever approach)
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=filter_metadata,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results (following the notebook's format)
            search_results = []
            if results["documents"] and results["documents"][0]:
                for i in range(len(results["documents"][0])):
                    similarity_score = 1 - results["distances"][0][i]  # Convert distance to similarity
                    
                    if similarity_score >= settings.similarity_threshold:
                        search_results.append({
                            "content": results["documents"][0][i],
                            "metadata": results["metadatas"][0][i],
                            "similarity_score": similarity_score
                        })
            
            logger.info(f"Found {len(search_results)} relevant documents for query")
            return search_results
            
        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            raise
    
    async def list_documents(self) -> List[Dict[str, Any]]:
        """List all processed documents"""
        try:
            # Get all documents from collection
            results = self.collection.get(include=["metadatas"])
            
            # Group by document_id
            documents = {}
            for metadata in results["metadatas"]:
                doc_id = metadata["document_id"]
                if doc_id not in documents:
                    documents[doc_id] = {
                        "document_id": doc_id,
                        "filename": metadata["filename"],
                        "document_type": metadata["document_type"],
                        "chunk_count": metadata["chunk_count"],
                        "created_at": metadata["created_at"]
                    }
            
            return list(documents.values())
            
        except Exception as e:
            logger.error(f"Error listing documents: {str(e)}")
            raise
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete document from ChromaDB"""
        try:
            # Get all chunks for this document
            results = self.collection.get(
                where={"document_id": document_id},
                include=["metadatas"]
            )
            
            if results["ids"]:
                self.collection.delete(ids=results["ids"])
                logger.info(f"Deleted document {document_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")
            raise
    
    def persist_collection(self):
        """Persist the ChromaDB collection (similar to notebook's persist())"""
        try:
            # ChromaDB with PersistentClient automatically persists
            logger.info("ChromaDB collection persisted automatically")
        except Exception as e:
            logger.error(f"Error persisting collection: {str(e)}")
    
    async def load_default_documents(self):
        """Load default troubleshooting documents"""
        try:
            # Create default Conga CPQ Turbo API troubleshooting document
            default_content = await self._create_default_document()
            
            # Check if default document already exists
            existing_docs = await self.list_documents()
            default_exists = any(doc["filename"] == "conga_cpq_turbo_troubleshooting.md" 
                               for doc in existing_docs)
            
            if not default_exists:
                await self.process_document(
                    content=default_content,
                    filename="conga_cpq_turbo_troubleshooting.md",
                    document_type="troubleshooting",
                    metadata={"version": "1.0", "default": True}
                )
                logger.info("Loaded default troubleshooting document")
                
                # Persist the collection after adding default documents
                self.persist_collection()
            
        except Exception as e:
            logger.error(f"Error loading default documents: {str(e)}")
    
    async def _create_default_document(self) -> str:
        """Create default Conga CPQ Turbo API troubleshooting document"""
        return '''# Conga CPQ Turbo API Troubleshooting Guide

## Overview
This guide provides troubleshooting steps for common issues with Conga CPQ Turbo APIs.

## Authentication Issues

### Bearer Token Problems
- **Issue**: 401 Unauthorized errors
- **Solution**: 
  1. Verify bearer token is not expired
  2. Check token format: `Bearer <token>`
  3. Ensure token has required scopes
  4. Regenerate token if necessary

### API Key Issues
- **Issue**: 403 Forbidden errors
- **Solution**:
  1. Verify API key is active
  2. Check API key permissions
  3. Ensure correct headers are sent

## API Endpoints

### Quote Management API
**Endpoint**: `POST /api/v1/quotes`
**Description**: Create a new quote
**Headers**: 
- `Authorization: Bearer <token>`
- `Content-Type: application/json`
**Payload Schema**:
```json
{
  "accountId": "string",
  "opportunityId": "string",
  "products": [
    {
      "productId": "string",
      "quantity": "number",
      "listPrice": "number"
    }
  ]
}
```

### Product Catalog API
**Endpoint**: `GET /api/v1/products`
**Description**: Retrieve product catalog
**Headers**: 
- `Authorization: Bearer <token>`
**Query Parameters**:
- `category`: Product category filter
- `status`: Product status (active/inactive)

### Pricing Engine API
**Endpoint**: `POST /api/v1/pricing/calculate`
**Description**: Calculate pricing for products
**Headers**: 
- `Authorization: Bearer <token>`
- `Content-Type: application/json`
**Payload Schema**:
```json
{
  "quoteId": "string",
  "products": [
    {
      "productId": "string",
      "quantity": "number"
    }
  ],
  "discountRules": ["string"]
}
```

### Configuration API
**Endpoint**: `POST /api/v1/configure`
**Description**: Configure product bundles
**Headers**: 
- `Authorization: Bearer <token>`
- `Content-Type: application/json`

## Common Error Codes

### 400 Bad Request
- **Cause**: Invalid request payload or missing required fields
- **Solution**: 
  1. Validate JSON schema
  2. Check required fields
  3. Verify data types

### 404 Not Found
- **Cause**: Resource not found (quote, product, etc.)
- **Solution**:
  1. Verify resource ID exists
  2. Check user permissions for resource
  3. Ensure resource is not soft-deleted

### 429 Rate Limit Exceeded
- **Cause**: Too many API requests
- **Solution**:
  1. Implement exponential backoff
  2. Reduce request frequency
  3. Contact support for rate limit increase

### 500 Internal Server Error
- **Cause**: Server-side error
- **Solution**:
  1. Retry request after delay
  2. Check API status page
  3. Contact technical support

## Performance Issues

### Slow Response Times
- **Cause**: Large data sets or complex calculations
- **Solution**:
  1. Use pagination for large results
  2. Implement caching where appropriate
  3. Optimize query parameters

### Timeout Errors
- **Cause**: Request taking too long to process
- **Solution**:
  1. Increase timeout settings
  2. Break large requests into smaller chunks
  3. Use asynchronous processing for bulk operations

## Best Practices

### API Usage
1. Always include proper error handling
2. Use exponential backoff for retries
3. Cache responses when appropriate
4. Monitor API usage and limits

### Security
1. Store bearer tokens securely
2. Rotate tokens regularly
3. Use HTTPS for all API calls
4. Never log sensitive data

### Troubleshooting Steps
1. Check API documentation for recent changes
2. Verify environment configuration
3. Test with minimal payload first
4. Check server logs for detailed error messages
5. Use API testing tools for debugging

## Contact Information
- Technical Support: support@conga.com
- API Documentation: https://docs.conga.com/cpq-turbo-api
- Status Page: https://status.conga.com
'''

    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the ChromaDB collection"""
        try:
            count = self.collection.count()
            return {
                "collection_name": settings.collection_name,
                "document_count": count,
                "vector_db_path": settings.vector_db_path,
                "embedding_model": "thenlper/gte-large"
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {str(e)}")
            return {}