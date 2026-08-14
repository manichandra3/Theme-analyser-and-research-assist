import json
import re
from typing import List, Optional

import google.generativeai as genai

from .config import RAGConfig
from .types import RetrievedChunk

RERANK_PROMPT = """You are a precision reranker for retrieved document passages.
Rank the {count} passages by how relevant each is to the query. Return ONLY a JSON
object with an ordered list of "indices" (the original 0-based positions),
best first. Example: {{"indices": [2, 0, 1]}}

Query: {query}

Passages:
{numbered}

JSON:
"""


class LLMReranker:
    """Cross-precision reranker using the generative model as a judge.

    Passes the top-N candidates to the LLM and asks for an ordering. Falls
    back to the fused retrieval score if the LLM call fails or returns
    unparseable output, so reranking never breaks the pipeline.
    """

    def __init__(self, api_key: str, config: Optional[RAGConfig] = None):
        genai.configure(api_key=api_key)
        self.config = config or RAGConfig()
        self.model = genai.GenerativeModel(self.config.generator_model)

    def _parse_indices(self, text: str) -> Optional[List[int]]:
        match = re.search(r"\{.*?\}", text, re.DOTALL)
        if not match:
            return None
        try:
            data = json.loads(match.group(0))
            indices = data.get("indices") or data.get("indices_list") or []
            return [int(i) for i in indices]
        except Exception:
            return None

    def rerank(self, query: str, candidates: List[RetrievedChunk],
               top_n: int) -> List[RetrievedChunk]:
        pool = candidates[:top_n]
        if not pool or len(pool) < 2:
            return candidates

        numbered = "\n".join(
            f"[{i}] {c.chunk.text[:500]}" for i, c in enumerate(pool)
        )
        prompt = RERANK_PROMPT.format(query=query, numbered=numbered)
        try:
            resp = self.model.generate_content(prompt)
            indices = self._parse_indices(resp.text or "")
        except Exception:
            indices = None

        if indices is None:
            ordered = sorted(candidates, key=lambda c: -c.dense_score)
            for i, rc in enumerate(ordered):
                rc.rank = i
            return ordered

        seen = set()
        reordered = []
        for i in indices:
            if i in seen or not (0 <= i < len(pool)):
                continue
            seen.add(i)
            rc = pool[i]
            rc.rerank_score = float(len(pool) - len(seen) + 1)
            reordered.append(rc)

        for i, rc in enumerate(pool):
            if i not in seen:
                reordered.append(rc)

        reordered += [c for c in candidates[top_n:]]
        for rank, rc in enumerate(reordered):
            rc.rank = rank
        return reordered


class ScoreReranker:
    """No-op reranker that preserves the hybrid fusion order."""

    def rerank(self, query: str, candidates: List[RetrievedChunk],
               top_n: int) -> List[RetrievedChunk]:
        for i, rc in enumerate(candidates):
            rc.rank = i
        return candidates


def get_reranker(api_key: str, config: Optional[RAGConfig] = None):
    if config and not config.use_rerank:
        return ScoreReranker()
    return LLMReranker(api_key, config)