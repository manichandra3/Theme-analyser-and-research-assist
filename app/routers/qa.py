from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from services.qa_service import answer_question

router = APIRouter()

@router.get("/ask", response_model=List[Dict[str, str]])
async def ask_question(question: str, k: int = 5):
    """
    Ask a question about the documents and get an answer with citations and theme analysis.
    
    Args:
        question: The question to ask
        k: Number of chunks to retrieve (default: 5)
    
    Returns:
        List of dictionaries containing the answer, citations, and themes in table format:
        [
            {
                "doc_id": "Answer",
                "content": "The answer text",
                "page": "",
                "paragraph": ""
            },
            {
                "doc_id": "1",
                "content": "Cited text",
                "page": "1",
                "paragraph": "1"
            },
            {
                "doc_id": "Theme 1",
                "content": "Theme summary",
                "page": "",
                "paragraph": ""
            },
            {
                "doc_id": "1",
                "content": "Supporting evidence",
                "page": "2",
                "paragraph": "3"
            },
            ...
        ]
    """
    try:
        return await answer_question(question, k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
