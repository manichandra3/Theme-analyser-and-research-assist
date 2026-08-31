import time
from typing import List

import google.generativeai as genai
from typing import Optional

from .config import RAGConfig
from .types import GenerationResult, RetrievedChunk

QA_PROMPT = """You are a document-answering assistant. Answer the user's question using ONLY
the provided context passages. Cite every claim with the passage tag that appears at the
start of the passage (e.g. [D:d P:p C:c]). If the context does not contain the answer,
say so honestly.

Context passages:
{context}

Question: {question}

Answer with inline citations:"""


def format_context(chunks: List[RetrievedChunk]) -> str:
    parts = []
    for rc in chunks:
        c = rc.chunk
        tag = f"[D:{c.doc_id} P:{c.page} C:{c.chunk_num}]"
        parts.append(f"{tag}\n{c.text}")
    return "\n\n".join(parts)


class Generator:
    """LLM answer generation grounded in retrieved chunks with citations."""

    def __init__(self, api_key: str, config: Optional[RAGConfig] = None):
        genai.configure(api_key=api_key)
        self.config = config or RAGConfig()
        self.model = genai.GenerativeModel(self.config.generator_model)

    def generate(self, question: str, chunks: List[RetrievedChunk]) -> GenerationResult:
        start = time.monotonic()
        if not chunks:
            return GenerationResult(
                answer="No relevant context was retrieved to answer the question.",
                timing_ms=(time.monotonic() - start) * 1000,
            )
        prompt = QA_PROMPT.format(
            context=format_context(chunks),
            question=question,
        )
        try:
            resp = self.model.generate_content(prompt)
            answer = (resp.text or "").strip()
        except Exception:
            answer = "Unable to generate an answer at this time."
        return GenerationResult(
            answer=answer,
            citations=[c.chunk.id for c in chunks],
            timing_ms=(time.monotonic() - start) * 1000,
        )
