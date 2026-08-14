from typing import List, Optional

import google.generativeai as genai

from .config import RAGConfig
from .types import QueryPlan

REWRITE_PROMPT = """You are a query-expansion specialist for a retrieval system.
Given a user question, generate {n} alternative phrasings of the question that would
help retrieve relevant document passages. Each variant should express the same
information need differently (paraphrase, more specific terms, sub-questions).

Question: {question}

Return ONLY a numbered list, one variant per line, e.g.:
1. ...
2. ...
"""

HYDE_PROMPT = """You are asked to draft a hypothetical passage from a set of research
documents that would answer the question below. Write a short, self-contained
passage (2-4 sentences) as if it were an excerpt from the documents. Do NOT
answer in first person.

Question: {question}
"""


class QueryRewriter:
    """Expands a question into retrieval-friendly variants.

    Two modern techniques:
    - Multi-query expansion (rewrites of the original question)
    - HyDE (Hypothetical Document Embeddings): a synthetic passage that
      steers dense retrieval toward semantically similar content.
    """

    def __init__(self, api_key: str, config: Optional[RAGConfig] = None):
        genai.configure(api_key=api_key)
        self.config = config or RAGConfig()
        self.model = genai.GenerativeModel(self.config.generator_model)

    def _safe_generate(self, prompt: str) -> str:
        try:
            resp = self.model.generate_content(prompt)
            return (resp.text or "").strip()
        except Exception:
            return ""

    def _parse_numbered_list(self, text: str) -> List[str]:
        lines = []
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            for prefix in ("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9."):
                if stripped.startswith(prefix):
                    stripped = stripped[len(prefix):].strip()
                    break
            lines.append(stripped)
        return lines

    def _rewrites(self, question: str) -> List[str]:
        if not self.config.use_rewrite:
            return []
        prompt = REWRITE_PROMPT.format(n=self.config.n_rewrites, question=question)
        raw = self._safe_generate(prompt)
        parsed = self._parse_numbered_list(raw)
        return [p for p in parsed if p and p.lower() != question.lower()][: self.config.n_rewrites]

    def _hyde(self, question: str) -> str:
        if not self.config.use_hyde:
            return ""
        return self._safe_generate(HYDE_PROMPT.format(question=question))

    def plan(self, question: str) -> QueryPlan:
        return QueryPlan(
            original=question,
            rewrites=self._rewrites(question),
            hyde_doc=self._hyde(question) or None,
        )