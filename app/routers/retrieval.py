from fastapi import APIRouter, HTTPException, Query
from app.services.embeddings import search
from app.services.storage import get_document_by_id
from typing import Optional, List, Dict

router = APIRouter()


@router.get("/{document_id}")
async def get_document(document_id: int):
    """
    Get full document content and metadata by ID
    """
    document = get_document_by_id(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@router.get("/", response_model=Dict)
async def retrieve(
    query: str = Query(..., min_length=1, description="Search query text"),
    top_n: int = Query(default=5, ge=1, le=20, description="Number of results to return"),
    include_content: bool = Query(default=False, description="Include full document content"),
    chunk_size: int = Query(default=500, ge=100, le=2000, description="Size of text chunk to return")
):
    """
    Search for documents with optional content retrieval
    
    Returns:
    - query: Original search query
    - results: List of matching documents with relevance scores
    - total: Number of results found
    """
    try:
        results = search(query, top_n)
        
        if not results:
            return {
                "query": query,
                "results": [],
                "total": 0,
                "message": "No matching documents found"
            }
            
        if not include_content:
            # Remove full content from response if not requested
            for doc in results:
                doc.pop("content", None)
        
        return {
            "query": query,
            "results": results,
            "total": len(results),
            "message": f"Found {len(results)} matching documents"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error during search: {str(e)}"
        )
