from typing import List, Dict, Any, Optional

from ..rag.chunking import get_chunker, estimate_tokens
from ..rag.config import RAGConfig
from ..rag.embeddings import get_embedder
from ..core.config import settings
from ..rag.store import ChromaAdapter

# Shared Chroma-backed adapter used by ingestion and retrieval.
_adapter = ChromaAdapter()

# Chunker and embedder mirroring the RAG pipeline defaults.
_chunker = get_chunker(RAGConfig().chunking_strategy, max_tokens=RAGConfig().chunk_size_tokens)
_embedder = get_embedder(settings.GEMINI_API_KEY)


def get_embedding(text: str) -> List[float]:
    """Get embedding for text using the configured embedder."""
    return _embedder.embed(text)


def approximate_tokens(text: str) -> int:
    """Approximate token count using character-based estimation."""
    return estimate_tokens(text)


def split_text_into_chunks(text: str, max_tokens: int = 500) -> List[str]:
    """Split text into chunks using the recursive chunker."""
    chunks = _chunker.chunk("_", 0, text)
    return [c.text for c in chunks]


def store_document_chunks(doc_id: str, page_num: int, chunks: List[str]) -> None:
    """Store document chunks in the vector database."""
    from ..rag.types import Chunk

    objs = [
        Chunk(
            id=f"{doc_id}_p{page_num}_c{i}",
            text=text,
            doc_id=doc_id,
            page=page_num,
            chunk_num=i,
            token_count=estimate_tokens(text),
        )
        for i, text in enumerate(chunks)
    ]
    embeddings = _embedder.embed_many([c.text for c in objs])
    _adapter.add_chunks(objs, embeddings)


def search_similar_chunks(query: str, k: int = 5) -> List[Dict[str, Any]]:
    """Search for similar chunks using dense semantic search."""
    emb = _embedder.embed(query)
    results = _adapter.dense_search(emb, k)
    return [
        {
            "text": rc.chunk.text,
            "metadata": rc.chunk.metadata,
            "distance": 1.0 - rc.dense_score,
        }
        for rc in results
    ]


def hybrid_search(query: str, k: int = 5) -> List[Dict[str, Any]]:
    """Hybrid search using dense embeddings + BM25 with RRF fusion."""
    from ..rag.retrieval import RetrievalPipeline
    from ..rag.types import QueryPlan

    pipeline = RetrievalPipeline(_embedder, _adapter)
    result = pipeline.retrieve(QueryPlan(original=query))
    return [
        {
            "text": rc.chunk.text,
            "metadata": rc.chunk.metadata,
            "dense_score": rc.dense_score,
            "sparse_score": rc.sparse_score,
            "sources": rc.sources,
        }
        for rc in result.chunks[:k]
    ]


collection = _adapter.collection