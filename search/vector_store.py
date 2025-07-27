"""
Vector store operations for semantic search
"""
import logging
import os
import numpy as np
from openai import OpenAI
from config.settings import OPENAI_API_KEY, EMBED_MODEL
from database.models import query_vectors

# Initialize OpenAI client
client = None


def embed(text: str) -> np.ndarray:
    """Generate embedding for text using OpenAI API"""
    global client
    
    # Initialize client if not already done
    if not client:
        if OPENAI_API_KEY and OPENAI_API_KEY != "sk-your-actual-openai-key-here":
            try:
                client = OpenAI(api_key=OPENAI_API_KEY)
                logging.info("OpenAI client initialized successfully")
            except Exception as e:
                logging.error(f"Failed to initialize OpenAI client: {e}")
                client = None
        else:
            logging.warning("OpenAI API key not set or invalid")
            client = None
    
    if not client:
        logging.warning("OpenAI client not initialized. Please set OPENAI_API_KEY in .env file")
        # Return zero vector as fallback
        return np.zeros(1536, dtype=np.float32)
    
    try:
        resp = client.embeddings.create(model=EMBED_MODEL, input=[text[:8000]])
        return np.array(resp.data[0].embedding, dtype=np.float32)
    except Exception as e:
        logging.error(f"Embedding error: {e}")
        # Return zero vector as fallback
        return np.zeros(1536, dtype=np.float32)


def search(query: str, top_k: int = 5):
    """
    Perform semantic search on the vector database
    Returns formatted results for the API
    """
    try:
        # Generate embedding for query
        vec = embed(query)
        
        # Query vector database
        results = query_vectors(vec, top_k=top_k)
        
        # Format results
        payload = [
            {
                "url": r["url"],
                "title": r["title"] or "Untitled",
                "snippet": (r["text"][:300] + "..." if len(r["text"]) > 300 else r["text"]) if r["text"] else "No content available",
                "score": round(score, 3),
            }
            for r, score in results
        ]
        
        return payload
    
    except Exception as e:
        logging.error(f"Search error: {e}")
        return [] 