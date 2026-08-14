from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Chunk:
    """A single retrievable unit of text with its provenance metadata."""

    id: str
    text: str
    doc_id: str
    page: int
    chunk_num: int
    start_char: int = 0
    end_char: int = 0
    token_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RetrievedChunk:
    """A chunk returned by the retriever along with its scores."""

    chunk: Chunk
    dense_score: float = 0.0
    sparse_score: float = 0.0
    fused_score: float = 0.0
    rerank_score: float = 0.0
    rank: int = 0
    sources: List[str] = field(default_factory=list)


@dataclass
class QueryPlan:
    """Expanded query strategy: original + rewrites + HyDE document."""

    original: str
    rewrites: List[str] = field(default_factory=list)
    hyde_doc: Optional[str] = None

    def variants(self) -> List[str]:
        parts = [self.original]
        parts.extend(self.rewrites)
        if self.hyde_doc:
            parts.append(self.hyde_doc)
        return parts


@dataclass
class RetrievalResult:
    """Output of the retrieval stage with optional ranking metrics."""

    query: str
    chunks: List[RetrievedChunk] = field(default_factory=list)
    timing_ms: float = 0.0
    metrics: Dict[str, float] = field(default_factory=dict)


@dataclass
class GenerationResult:
    """Output of the generation stage with quality metrics."""

    answer: str = ""
    citations: List[str] = field(default_factory=list)
    timing_ms: float = 0.0
    metrics: Dict[str, float] = field(default_factory=dict)
    raw: str = ""


@dataclass
class RAGResult:
    """Complete end-to-end pipeline result."""

    question: str
    retrieval: RetrievalResult = field(default_factory=RetrievalResult)
    generation: GenerationResult = field(default_factory=GenerationResult)

    def metrics(self) -> Dict[str, float]:
        merged = dict(self.retrieval.metrics)
        merged.update(self.generation.metrics)
        return merged