from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from services.vector_store import (
    search_similar_chunks,
    store_document_chunks,
    split_text_into_chunks,
    hybrid_search,
)

router = APIRouter()


@router.get("/search", response_model=List[Dict[str, Any]])
async def semantic_search(query: str, k: int = 5, mode: str = "hybrid"):
    """
    Perform semantic or hybrid search on document chunks.

    Args:
        query: The search query
        k: Number of results to return (default: 5)
        mode: "hybrid" (dense + BM25 with RRF) or "dense"

    Returns:
        List of similar chunks with metadata and similarity scores.
    """
    try:
        if mode == "hybrid":
            return hybrid_search(query, k)
        return search_similar_chunks(query, k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test/setup")
async def setup_test_data():
    """
    Add some test documents to the vector store.
    """
    test_documents = [
        {
            "doc_id": "test1",
            "page": 1,
            "content": """
            Artificial Intelligence (AI) is transforming the way we live and work. 
            Machine learning algorithms can now process vast amounts of data to make predictions and decisions.
            Deep learning, a subset of machine learning, uses neural networks to learn from examples.
            """
        },
        {
            "doc_id": "test2",
            "page": 1,
            "content": """
            Python is a versatile programming language known for its simplicity and readability.
            It's widely used in data science, web development, and automation.
            The language's extensive library ecosystem makes it a popular choice for developers.
            """
        },
        {
            "doc_id": "test3",
            "page": 1,
            "content": """
            Vector databases are specialized databases designed for storing and searching vector embeddings.
            They enable efficient similarity search and are crucial for AI applications.
            Popular vector databases include Chroma, FAISS, and Qdrant.
            """
        }
    ]
    
    try:
        for doc in test_documents:
            chunks = split_text_into_chunks(doc["content"])
            store_document_chunks(doc["doc_id"], doc["page"], chunks)
        return {"message": "Test data added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
