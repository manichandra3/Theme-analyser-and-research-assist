from dataclasses import dataclass, field
from typing import List


@dataclass
class RAGConfig:
    """Runtime configuration for every stage of the RAG pipeline.

    Each stage (chunking, embedding, retrieval, rewriting, reranking,
    generation, evaluation) reads its knobs from this object so the whole
    pipeline can be tuned from one place and compared across experiments.
    """

    embedding_model: str = "embedding-001"
    generator_model: str = "gemini-2.0-flash"
    judge_model: str = "gemini-2.0-flash"

    # Chunking
    chunking_strategy: str = "recursive"
    chunk_size_tokens: int = 500
    chunk_overlap_tokens: int = 50

    # Retrieval
    dense_k: int = 20
    sparse_k: int = 20
    final_k: int = 5
    rrf_k: int = 60
    use_hybrid: bool = True
    use_mmr: bool = False
    mmr_lambda: float = 0.7

    # Query understanding
    use_rewrite: bool = True
    n_rewrites: int = 2
    use_hyde: bool = True

    # Reranking
    use_rerank: bool = True
    rerank_top_n: int = 15

    # Generation
    include_citations: bool = True
    max_answer_tokens: int = 1024

    # Evaluation
    evaluate_generation: bool = False
    eval_k: int = 5
    eval_scores: List[str] = field(default_factory=lambda: [
        "recall",
        "precision",
        "mrr",
        "ndcg",
        "hit_rate",
    ])