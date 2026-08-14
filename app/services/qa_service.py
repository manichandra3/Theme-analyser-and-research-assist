from typing import List, Dict, Any

from ..core.config import settings
from ..db.database import SessionLocal
from ..db.models import Document
from .theme_synthesizer import synthesize_themes
from ..rag.pipeline import RAGPipeline
from ..rag.config import RAGConfig
from ..rag.metrics import retrieval_metrics


def get_all_document_content() -> List[Dict[str, Any]]:
    """Get all document content from the database."""
    db = SessionLocal()
    try:
        documents = db.query(Document).all()
        all_content = []

        for doc in documents:
            for page in doc.pages:
                page_content = {
                    "doc_id": str(doc.id),
                    "page": page.page_number,
                    "content": page.content,
                    "paragraphs": [
                        {
                            "paragraph_number": p.paragraph_number,
                            "content": p.content,
                        }
                        for p in page.paragraphs
                    ],
                }
                all_content.append(page_content)

        return all_content
    finally:
        db.close()


def _retrieved_to_rows(chunks) -> List[Dict[str, str]]:
    """Convert retrieved chunks into the table row format the frontend uses."""
    rows = []
    for rc in chunks:
        c = rc.chunk
        rows.append({
            "doc_id": c.doc_id,
            "content": c.text,
            "page": str(c.page),
            "paragraph": str(c.chunk_num),
        })
    return rows


async def answer_question(question: str, k: int = 5) -> List[Dict[str, str]]:
    """
    Answer a question using the modular RAG pipeline.

    Runs query rewriting, hybrid (dense + BM25) retrieval, reranking and
    LLM generation, then formats the result into the table structure used by
    the frontend (answer row + citation rows + theme rows).
    """
    all_content = get_all_document_content()

    if not all_content:
        return [{
            "doc_id": "Answer",
            "content": "No documents have been processed yet. Please upload some documents first.",
            "page": "",
            "paragraph": "",
        }]

    config = RAGConfig(final_k=k)
    pipeline = RAGPipeline(settings.GEMINI_API_KEY, config)
    result = pipeline.run(question)

    answer_rows = [{
        "doc_id": "Answer",
        "content": result.generation.answer,
        "page": "",
        "paragraph": "",
    }]
    answer_rows += _retrieved_to_rows(result.retrieval.chunks)

    theme_rows = await synthesize_themes(answer_rows)

    return answer_rows + theme_rows