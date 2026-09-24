"""
Knowledge Base Routes - RAG endpoints for ChatGPT plugin
Provides /api/chat, /api/knowledge/search, and /api/knowledge/get endpoints
"""
import logging
import os
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field
from src.auth.operator import require_operator

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

from ..services.ai_runtime.embedding_runtime import generate_text_embedding


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str
    limit: int = Field(default=5, ge=1, le=100)


def _owned_chunk(chunk: dict | None, user_id: str) -> bool:
    """Unscoped legacy records and conflicting owner aliases stay private."""
    return bool(chunk and chunk.get("user_id") == user_id and all(
        key not in chunk or chunk[key] == user_id
        for key in ("userId", "firebase_uid", "uid", "ownerId")
    ))


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
    """Generate embedding for text using the centralized embedding runtime."""
    return await generate_text_embedding(text)


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
async def chat_retrieve(request: ChatRequest, claims: dict = Depends(require_operator)):
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
            return await _keyword_search(request.query, request.limit or 5, claims["uid"])
        
        # Scope the database query before scanning or scoring any content.
        chunks_ref = db.collection("knowledge_chunks").where("user_id", "==", claims["uid"])
        docs = chunks_ref.limit(1000).stream()  # Limit for performance
        
        chunks_with_scores = []
        for doc in docs:
            chunk_data = doc.to_dict()
            if not _owned_chunk(chunk_data, claims["uid"]):
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
    
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error in chat retrieval: {e}")
        raise HTTPException(status_code=500, detail="Retrieval failed") from None


async def _keyword_search(query: str, limit: int, user_id: str) -> Dict[str, Any]:
    """Fallback keyword search if embeddings are not available"""
    if not db or not firebase_initialized:
        raise HTTPException(status_code=503, detail="Database not available")
    
    query_lower = query.lower()
    chunks_ref = db.collection("knowledge_chunks").where("user_id", "==", user_id)
    docs = chunks_ref.limit(1000).stream()
    
    matching_chunks = []
    for doc in docs:
        chunk_data = doc.to_dict()
        if not _owned_chunk(chunk_data, user_id):
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
    limit: int = Query(10, ge=1, le=100, description="Maximum number of results"),
    claims: dict = Depends(require_operator),
):
    """
    Search knowledge by keyword.
    Returns chunks that contain the search query.
    """
    return await _keyword_search(query, limit, claims["uid"])


@router.get("/knowledge/get")
async def knowledge_get(
    chunk_id: str = Query(..., min_length=1, pattern=r"^[^/]+$", description="Chunk ID to retrieve"),
    claims: dict = Depends(require_operator),
):
    """
    Get a specific chunk by ID.
    """
    if not db or not firebase_initialized:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        doc_ref = db.collection("knowledge_chunks").document(chunk_id)
        doc = doc_ref.get()
        
        chunk_data = doc.to_dict() if doc.exists else None
        if not _owned_chunk(chunk_data, claims["uid"]):
            raise HTTPException(status_code=404, detail="Chunk not found")
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
        raise HTTPException(status_code=500, detail="Failed to retrieve chunk") from None
