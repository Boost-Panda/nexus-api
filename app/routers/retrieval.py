from fastapi import APIRouter, HTTPException, Query
from app.services.embeddings import search, model
from app.services.memory_walker import MemoryWalker
from app.services.query_refiner import QueryRefiner
from typing import Optional, List, Dict

router = APIRouter()

# Initialize services
memory_walker = MemoryWalker(model)
query_refiner = QueryRefiner(model, memory_walker)

@router.get("/enhanced")
async def enhanced_retrieve(
    query: str = Query(..., description="Search query"),
    top_n: int = Query(default=5, ge=1, le=20),
    use_memory_tree: bool = Query(default=True),
    refine_query: bool = Query(default=True)
):
    """
    Enhanced retrieval using MemoryWalker and query refinement
    """
    try:
        if refine_query:
            refined_query, confidence = await query_refiner.refine_query(query)
            if confidence > 0.8:
                query = refined_query
        
        results = search(query, top_n)
        
        if use_memory_tree:
            # Enhance results with hierarchical context
            for result in results:
                memory_tree = memory_walker.build_memory_tree(result["content"])
                result["context_hierarchy"] = _serialize_memory_tree(memory_tree)
        
        return {
            "query": query,
            "results": results,
            "total": len(results)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def _serialize_memory_tree(node):
    """Convert MemoryNode to JSON-serializable format"""
    return {
        "summary": node.summary,
        "children": [_serialize_memory_tree(child) for child in node.children]
    }
