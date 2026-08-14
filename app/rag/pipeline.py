from typing import List, Optional

from .config import RAGConfig
from .embeddings import get_embedder
from .generation import Generator
from .judges import LLMJudge
from .reranking import get_reranker
from .retrieval import RetrievalPipeline
from .rewriting import QueryRewriter
from .store import ChromaAdapter
from .types import RAGResult


class RAGPipeline:
    """Orchestrates the modular RAG stages end to end.

    Flow: query understanding (rewrite + HyDE) -> hybrid retrieval (dense +
    BM25 via RRF) -> optional rerank -> generation. Each stage is swappable
    and configured through a single RAGConfig.
    """

    def __init__(self, api_key: str, config: Optional[RAGConfig] = None,
                 adapter: Optional[ChromaAdapter] = None):
        self.config = config or RAGConfig()
        self.adapter = adapter or ChromaAdapter()
        self.embedder = get_embedder(api_key, self.config.embedding_model)
        self.rewriter = QueryRewriter(api_key, self.config)
        self.retriever = RetrievalPipeline(self.embedder, self.adapter, self.config)
        self.reranker = get_reranker(api_key, self.config)
        self.generator = Generator(api_key, self.config)
        self.judge = LLMJudge(api_key, self.config)

    def run(self, question: str) -> RAGResult:
        plan = self.rewriter.plan(question)
        retrieval = self.retriever.retrieve(plan)
        reranked = self.reranker.rerank(
            question, retrieval.chunks, self.config.rerank_top_n
        )
        retrieval.chunks = reranked[: self.config.final_k]
        generation = self.generator.generate(question, retrieval.chunks)

        result = RAGResult(question=question, retrieval=retrieval, generation=generation)

        # Generation quality metrics (LLM-judged) — opt-in to avoid extra calls.
        if self.config.evaluate_generation:
            result.generation.metrics = self.judge.evaluate(
                question,
                generation.answer,
                [c.chunk.text for c in retrieval.chunks],
            )
        return result