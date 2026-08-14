from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from ..services.evaluation_service import run_retrieval_evaluation, run_generation_evaluation

router = APIRouter()


class RetrievalCase(BaseModel):
    question: str
    relevant_chunk_ids: List[str] = []


class RetrievalEvalRequest(BaseModel):
    test_cases: List[RetrievalCase]
    eval_k: int = 5


class GenerationCase(BaseModel):
    question: str
    reference_answer: str = ""


class GenerationEvalRequest(BaseModel):
    test_cases: List[GenerationCase]
    final_k: int = 5


@router.post("/evaluate/retrieval")
async def evaluate_retrieval(request: RetrievalEvalRequest):
    """
    Evaluate retrieval quality against ground-truth chunk ids.

    Returns Recall@k, Precision@k, MRR, NDCG@k and hit-rate averaged across
    the supplied test cases. Useful for comparing chunking strategies,
    retrieval modes (dense vs hybrid) and k values.
    """
    try:
        cases = [c.model_dump() for c in request.test_cases]
        return run_retrieval_evaluation(cases, request.eval_k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/evaluate/generation")
async def evaluate_generation(request: GenerationEvalRequest):
    """
    Evaluate end-to-end generation quality using LLM-as-judge metrics.

    Reports faithfulness (groundedness of the answer in retrieved context)
    and answer relevance for each question in the suite.
    """
    try:
        cases = [c.model_dump() for c in request.test_cases]
        return run_generation_evaluation(cases, request.final_k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))