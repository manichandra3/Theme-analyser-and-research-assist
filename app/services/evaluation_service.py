from typing import Dict, List, Optional

from ..core.config import settings
from ..rag.config import RAGConfig
from ..rag.judges import LLMJudge
from ..rag.metrics import retrieval_metrics
from ..rag.pipeline import RAGPipeline


def run_retrieval_evaluation(test_cases: List[Dict], eval_k: int = 5) -> Dict:
    """Run retrieval-only metrics against labeled ground-truth chunk ids.

    Each test case: {"question": str, "relevant_ids": [chunk_id, ...]}
    Multi-question metrics are averaged across the suite.
    """
    config = RAGConfig(final_k=eval_k, use_rewrite=False, use_hyde=False,
                       use_rerank=False, use_mmr=False)
    pipeline = RAGPipeline(settings.GEMINI_API_KEY, config)
    pipeline.retriever.config.use_rewrite = False
    pipeline.retriever.config.use_hyde = False

    per_question = []
    totals: Dict[str, float] = {}
    for case in test_cases:
        result = pipeline.run(case["question"])
        ranked = [rc.chunk.id for rc in result.retrieval.chunks]
        relevant = case.get("relevant_chunk_ids", [])
        metrics = retrieval_metrics(ranked, relevant, eval_k)
        per_question.append({
            "question": case["question"],
            "relevant_chunk_ids": relevant,
            "retrieved_chunk_ids": ranked,
            "metrics": metrics,
        })
        for key, value in metrics.items():
            totals[key] = totals.get(key, 0.0) + value

    n = max(1, len(test_cases))
    averages = {key: round(value / n, 4) for key, value in totals.items()}
    return {
        "eval_k": eval_k,
        "num_questions": len(test_cases),
        "averages": averages,
        "per_question": per_question,
    }


def run_generation_evaluation(test_cases: List[Dict], final_k: int = 5) -> Dict:
    """Run end-to-end generation evaluation with LLM-judged metrics.

    Each test case: {"question": str, "reference_answer": str}.
    Faithfulness is judged against the retrieved context; answer relevance
    is judged against the reference answer.
    """
    config = RAGConfig(final_k=final_k)
    config.evaluate_generation = True
    pipeline = RAGPipeline(settings.GEMINI_API_KEY, config)
    judge = LLMJudge(settings.GEMINI_API_KEY, config)

    results = []
    for case in test_cases:
        result = pipeline.run(case["question"])
        context = [c.chunk.text for c in result.retrieval.chunks]
        reference = case.get("reference_answer", result.generation.answer)
        metrics = judge.evaluate(case["question"], reference, context)
        results.append({
            "question": case["question"],
            "answer": result.generation.answer,
            "context_chunks": len(context),
            "metrics": metrics,
        })

    return {
        "num_questions": len(results),
        "final_k": final_k,
        "results": results,
    }