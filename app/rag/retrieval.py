import time
from typing import Dict, List, Optional

from .bm25 import BM25Index
from .config import RAGConfig
from .embeddings import Embedder
from .types import Chunk, QueryPlan, RetrievedChunk, RetrievalResult


def cosine(a: List[float], b: List[float]) -> float:
    """Pure-Python cosine similarity."""
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5 or 1.0
    nb = sum(y * y for y in b) ** 0.5 or 1.0
    return dot / (na * nb)


class VectorStoreAdapter:
    """Interface decoupling retrieval from the concrete vector database."""

    def all_chunks(self) -> Dict[str, Chunk]:
        raise NotImplementedError

    def dense_search(self, query_embedding: List[float], k: int) -> List[RetrievedChunk]:
        raise NotImplementedError


class RetrievalPipeline:
    """Hybrid retrieval: dense embeddings + sparse BM25 fused by RRF.

    Consumes a QueryPlan (original + rewrites + HyDE doc), runs each variant
    through dense + sparse retrieval, fuses scores with Reciprocal Rank
    Fusion, then optionally applies MMR for diversity.
    """

    def __init__(self, embedder: Embedder, adapter: VectorStoreAdapter,
                 config: Optional[RAGConfig] = None):
        self.embedder = embedder
        self.adapter = adapter
        self.config = config or RAGConfig()
        self._bm25_cache: Optional[BM25Index] = None

    def _chunks(self) -> Dict[str, Chunk]:
        return self.adapter.all_chunks()

    def _bm25(self) -> BM25Index:
        if self._bm25_cache is None:
            index = BM25Index()
            index.build({cid: c.text for cid, c in self._chunks().items()})
            self._bm25_cache = index
        return self._bm25_cache

    def _rrf(self, dense: List[str], sparse: List[str], k: int) -> List[str]:
        scores: Dict[str, float] = {}
        for ranking in (dense, sparse):
            for position, cid in enumerate(ranking):
                scores[cid] = scores.get(cid, 0.0) + 1.0 / (k + position + 1)
        ordered = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
        return [cid for cid, _ in ordered][: self.config.final_k]

    def retrieve(self, query: QueryPlan) -> RetrievalResult:
        start = time.monotonic()
        chunks = self._chunks()

        dense_scores: Dict[str, float] = {}
        sparse_scores: Dict[str, float] = {}

        for variant in query.variants():
            emb = self.embedder.embed(variant)
            for rc in self.adapter.dense_search(emb, self.config.dense_k):
                prev = dense_scores.get(rc.chunk.id)
                if prev is None or rc.dense_score > prev:
                    dense_scores[rc.chunk.id] = rc.dense_score
            for cid, score in self._bm25().search(variant, self.config.sparse_k):
                if score > sparse_scores.get(cid, 0.0):
                    sparse_scores[cid] = score

        if self.config.use_hybrid:
            fused = self._rrf(list(dense_scores), list(sparse_scores), self.config.rrf_k)
        else:
            fused = sorted(dense_scores, key=lambda c: dense_scores[c], reverse=True)

        merged: List[RetrievedChunk] = []
        for cid in fused:
            if cid not in chunks:
                continue
            merged.append(RetrievedChunk(
                chunk=chunks[cid],
                dense_score=dense_scores.get(cid, 0.0),
                sparse_score=sparse_scores.get(cid, 0.0),
                sources=(
                    ["dense", "sparse"]
                    if cid in dense_scores and cid in sparse_scores
                    else (["dense"] if cid in dense_scores else ["sparse"])
                ),
            ))

        if self.config.use_mmr:
            merged = self._mmr(query.original, merged, chunks)

        top = merged[: self.config.final_k]
        for i, rc in enumerate(top):
            rc.rank = i

        return RetrievalResult(
            query=query.original,
            chunks=top,
            timing_ms=(time.monotonic() - start) * 1000,
        )

    def _mmr(self, query: str, candidates: List[RetrievedChunk],
             chunks: Dict[str, Chunk]) -> List[RetrievedChunk]:
        if not candidates:
            return candidates
        q_emb = self.embedder.embed(query)
        selected: List[RetrievedChunk] = []
        remaining = list(candidates)
        while remaining:
            best, best_score = None, -float("inf")
            for cand in remaining:
                c_emb = self.embedder.embed(cand.chunk.text)
                relevance = cosine(q_emb, c_emb)
                diversity = max(
                    (cosine(c_emb, self.embedder.embed(s.chunk.text)) for s in selected),
                    default=0.0,
                )
                score = self.config.mmr_lambda * relevance - (1 - self.config.mmr_lambda) * diversity
                if score > best_score:
                    best_score, best = score, cand
            if best is None:
                break
            selected.append(best)
            remaining.remove(best)
        return selected