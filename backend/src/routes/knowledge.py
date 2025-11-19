"""
Knowledge Base Routes - RAG endpoints for ChatGPT plugin
Provides /api/chat, /api/knowledge/search, and /api/knowledge/get endpoints
"""
import logging
import os
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()

# Try to import Firestore
try:
    from src.config.firebase import db, firebase_initialized
except ImportError:
    try:
        from config.firebase import db, firebase_initialized
    except ImportError:
        db = None
        firebase_initialized = False
        logger.warning("Firebase not available for knowledge routes")

# Try to import OpenAI for embeddings
try:
    from openai import OpenAI
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) if os.getenv("OPENAI_API_KEY") else None
except ImportError:
    openai_client = None
    logger.warning("OpenAI client not available")


class ChatRequest(BaseModel):
    query: str
    limit: Optional[int] = 5


def _chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """Split text into overlapping chunks"""
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks


async def _generate_embedding(text: str) -> Optional[List[float]]:
    """Generate embedding for text using OpenAI"""
    if not openai_client:
        return None
    
    try:
        response = openai_client.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        return None


def _cosine_similarity(a: List[float], b: List[float]) -> float:
    """Calculate cosine similarity between two vectors"""
    if not a or not b or len(a) != len(b):
        return 0.0
    
    dot_product = sum(x * y for x, y in zip(a, b))
    magnitude_a = sum(x * x for x in a) ** 0.5
    magnitude_b = sum(x * x for x in b) ** 0.5
    
    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0
    
    return dot_product / (magnitude_a * magnitude_b)


@router.post("/chat")
async def chat_retrieve(request: ChatRequest):
    """
    Perform RAG retrieval against Firestore.
    Uses embeddings + vector search to return the most relevant chunks.
    """
    if not db or not firebase_initialized:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        # Generate embedding for query
        query_embedding = await _generate_embedding(request.query)
        if not query_embedding:
            # Fallback to keyword search if embeddings fail
            return await _keyword_search(request.query, request.limit or 5)
        
        # Get all knowledge chunks from Firestore
        chunks_ref = db.collection("knowledge_chunks")
        docs = chunks_ref.limit(1000).stream()  # Limit for performance
        
        chunks_with_scores = []
        for doc in docs:
            chunk_data = doc.to_dict()
            if not chunk_data:
                continue
            
            chunk_embedding = chunk_data.get("embedding")
            if not chunk_embedding:
                continue
            
            # Calculate similarity
            similarity = _cosine_similarity(query_embedding, chunk_embedding)
            
            chunks_with_scores.append({
                "chunk_id": doc.id,
                "text": chunk_data.get("text", ""),
                "metadata": chunk_data.get("metadata", {}),
                "similarity": similarity
            })
        
        # Sort by similarity and return top results
        chunks_with_scores.sort(key=lambda x: x["similarity"], reverse=True)
        top_chunks = chunks_with_scores[:request.limit or 5]
        
        return {
            "chunks": top_chunks,
            "query": request.query,
            "count": len(top_chunks)
        }
    
    except Exception as e:
        logger.exception(f"Error in chat retrieval: {e}")
        raise HTTPException(status_code=500, detail=f"Retrieval failed: {str(e)}")


async def _keyword_search(query: str, limit: int) -> Dict[str, Any]:
    """Fallback keyword search if embeddings are not available"""
    if not db or not firebase_initialized:
        raise HTTPException(status_code=503, detail="Database not available")
    
    query_lower = query.lower()
    chunks_ref = db.collection("knowledge_chunks")
    docs = chunks_ref.limit(1000).stream()
    
    matching_chunks = []
    for doc in docs:
        chunk_data = doc.to_dict()
        if not chunk_data:
            continue
        
        text = chunk_data.get("text", "").lower()
        if query_lower in text:
            matching_chunks.append({
                "chunk_id": doc.id,
                "text": chunk_data.get("text", ""),
                "metadata": chunk_data.get("metadata", {}),
                "similarity": 0.5  # Placeholder for keyword match
            })
    
    matching_chunks = matching_chunks[:limit]
    
    return {
        "chunks": matching_chunks,
        "query": query,
        "count": len(matching_chunks)
    }


@router.get("/knowledge/search")
async def knowledge_search(
    query: str = Query(..., description="Search query"),
    limit: int = Query(10, description="Maximum number of results")
):
    """
    Search knowledge by keyword.
    Returns chunks that contain the search query.
    """
    return await _keyword_search(query, limit)


@router.get("/knowledge/get")
async def knowledge_get(chunk_id: str = Query(..., description="Chunk ID to retrieve")):
    """
    Get a specific chunk by ID.
    """
    if not db or not firebase_initialized:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        doc_ref = db.collection("knowledge_chunks").document(chunk_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail=f"Chunk {chunk_id} not found")
        
        chunk_data = doc.to_dict()
        return {
            "chunk_id": doc.id,
            "text": chunk_data.get("text", ""),
            "metadata": chunk_data.get("metadata", {}),
            "embedding_available": bool(chunk_data.get("embedding"))
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error retrieving chunk: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve chunk: {str(e)}")

