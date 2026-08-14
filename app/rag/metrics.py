import math
import re
from typing import List, Set

from .config import RAGConfig
from .types import RAGResult


def recall_at_k(ranked: List[str], relevant: Set[str], k: int) -> float:
    """Fraction of relevant chunks found in the top-k."""
    if not relevant:
        return 0.0
    return sum(1 for c in ranked[:k] if c in relevant) / len(relevant)


def precision_at_k(ranked: List[str], relevant: Set[str], k: int) -> float:
    """Fraction of the top-k chunks that are relevant."""
    window = ranked[:k]
    if not window:
        return 0.0
    return sum(1 for c in window if c in relevant) / len(window)


def mrr_at_k(ranked: List[str], relevant: Set[str], k: int) -> float:
    """Mean Reciprocal Rank: 1/rank of the first relevant hit in top-k."""
    for position, cid in enumerate(ranked[:k], 1):
        if cid in relevant:
            return 1.0 / position
    return 0.0


def hit_rate_at_k(ranked: List[str], relevant: Set[str], k: int) -> float:
    """1 if any relevant chunk appears in top-k, else 0."""
    return 1.0 if any(c in relevant for c in ranked[:k]) else 0.0


def ndcg_at_k(ranked: List[str], relevant: Set[str], k: int) -> float:
    """Normalized Discounted Cumulative Gain with binary relevance."""
    dcg = 0.0
    for position, cid in enumerate(ranked[:k], 1):
        if cid in relevant:
            dcg += 1.0 / math.log2(position + 1)
    ideal = sum(1.0 / math.log2(p + 1) for p in range(1, min(k, len(relevant)) + 1))
    return dcg / ideal if ideal > 0 else 0.0


def retrieval_metrics(ranked_ids: List[str], relevant_ids: List[str], k: int) -> dict:
    """Compute the full retrieval metric suite at cutoff k."""
    relevant = set(relevant_ids)
    return {
        "recall": recall_at_k(ranked_ids, relevant, k),
        "precision": precision_at_k(ranked_ids, relevant, k),
        "mrr": mrr_at_k(ranked_ids, relevant, k),
        "ndcg": ndcg_at_k(ranked_ids, relevant, k),
        "hit_rate": hit_rate_at_k(ranked_ids, relevant, k),
    }


def _significant_words(text: str) -> List[str]:
    """Lowercased alpha words longer than a length cutoff, cached per call."""
    return [w for w in re.findall(r"[A-Za-z]{6,}", text.lower())]


def lexical_faithfulness(answer: str, context_chunks: List[str]) -> float:
    """Heuristic faithfulness proxy when no LLM judge is configured.

    Measures how much of each retrieved chunk's salient vocabulary appears
    in the generated answer. A rough but dependency-free groundless signal.
    """
    if not answer or not context_chunks:
        return 0.0
    answer_words = set(_significant_words(answer))
    if not answer_words:
        return 0.0
    best = 0.0
    for chunk in context_chunks:
        chunk_words = set(_significant_words(chunk))
        if not chunk_words:
            continue
        best = max(best, len(answer_words & chunk_words) / len(chunk_words))
    return min(1.0, best)