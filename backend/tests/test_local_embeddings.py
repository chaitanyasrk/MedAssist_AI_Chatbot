#!/usr/bin/env python3
"""
Test script for local embeddings with SentenceTransformer
Following the approach from the Jupyter notebook
"""

import os
import asyncio
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings as ChromaSettings

async def test_local_embeddings():
    """Test local embeddings setup"""
    
    print("🧪 Testing Local Embeddings Setup")
    print("=" * 50)
    
    try:
        # Test 1: Load SentenceTransformer model
        print("1️⃣ Loading SentenceTransformer model...")
        embedding_model = SentenceTransformer('thenlper/gte-large')
        print("✅ SentenceTransformer model loaded successfully!")
        
        # Test 2: Create embeddings
        print("\n2️⃣ Testing embedding creation...")
        test_text = "How do I fix 401 authentication errors?"
        embedding = embedding_model.encode(test_text)
        print(f"✅ Embedding created! Dimensions: {len(embedding)}")
        print(f"Sample values: {embedding[:5]}")
        
        # Test 3: Initialize ChromaDB
        print("\n3️⃣ Testing ChromaDB setup...")
        vector_db_path = "./data/vectordb"
        os.makedirs(vector_db_path, exist_ok=True)
        
        chroma_client = chromadb.PersistentClient(
            path=vector_db_path,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        collection = chroma_client.get_or_create_collection(
            name="test_collection",
            metadata={"hnsw:space": "cosine"}
        )
        print("✅ ChromaDB initialized successfully!")
        
        # Test 4: Store embeddings
        print("\n4️⃣ Testing document storage...")
        test_docs = [
            "How do I fix 401 authentication errors?",
            "What's the payload for creating a quote?",
            "How to handle rate limiting in API calls?"
        ]
        
        ids = []
        embeddings = []
        documents = []
        metadatas = []
        
        for i, doc in enumerate(test_docs):
            embedding = embedding_model.encode(doc)
            ids.append(f"doc_{i}")
            embeddings.append(embedding.tolist())
            documents.append(doc)
            metadatas.append({"doc_type": "test", "index": i})
        
        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        print(f"✅ Stored {len(test_docs)} documents in ChromaDB!")
        
        # Test 5: Search functionality
        print("\n5️⃣ Testing search functionality...")
        query = "authentication problems"
        query_embedding = embedding_model.encode(query)
        
        results = collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=2,
            include=["documents", "metadatas", "distances"]
        )
        
        print(f"✅ Search completed! Found {len(results['documents'][0])} results:")
        for i, (doc, distance) in enumerate(zip(results['documents'][0], results['distances'][0])):
            similarity = 1 - distance
            print(f"  {i+1}. Similarity: {similarity:.3f} - {doc}")
        
        # Test 6: Collection info
        print("\n6️⃣ Collection information...")
        count = collection.count()
        print(f"✅ Collection contains {count} documents")
        
        print("\n🎉 All tests passed! Local embeddings setup is working correctly.")
        print("\n📝 Next steps:")
        print("1. Update your .env file to remove AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
        print("2. Add EMBEDDING_MODEL_NAME=thenlper/gte-large")
        print("3. Install sentence-transformers: pip install sentence-transformers")
        print("4. Run your server: python -m uvicorn main:app --reload")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        
        if "sentence_transformers" in str(e).lower():
            print("\n💡 Install sentence-transformers:")
            print("pip install sentence-transformers")
        elif "chromadb" in str(e).lower():
            print("\n💡 Install chromadb:")
            print("pip install chromadb")
        elif "torch" in str(e).lower():
            print("\n💡 Install PyTorch:")
            print("pip install torch")
            
        return False

if __name__ == "__main__":
    asyncio.run(test_local_embeddings())