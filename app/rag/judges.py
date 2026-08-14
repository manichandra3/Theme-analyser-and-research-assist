import json
import re
from typing import List, Optional

import google.generativeai as genai

from .config import RAGConfig
from .metrics import lexical_faithfulness

FAITHFULNESS_PROMPT = """You are a strict groundedness grader. Judge whether the ANSWER
is fully supported by the provided CONTEXT. Consider only the context; the answer must
not introduce unsupported facts.

CONTEXT:
{context}

ANSWER:
{answer}

Return ONLY a JSON object: {{"faithfulness": 0.0_to_1.0, "unsupported_claims": "<short
explanation or empty string>"}}
"""

RELEVANCE_PROMPT = """You are grading how well an ANSWER responds to a QUESTION.
Focus only on whether the answer addresses the question, not on factual accuracy.

QUESTION: {question}

ANSWER: {answer}

Return ONLY a JSON object: {{"relevance": 0.0_to_1.0, "reason": "<short reason>"}}
"""


class LLMJudge:
    """LLM-as-judge for generation quality metrics.

    Faithfulness: does the answer stay grounded in the retrieved context?
    Answer relevance: does the answer address the question?

    Falls back to a lexical faithfulness proxy and a neutral relevance score
    when the LLM call fails, so evaluation never raises.
    """

    def __init__(self, api_key: str, config: Optional[RAGConfig] = None):
        genai.configure(api_key=api_key)
        self.config = config or RAGConfig()
        self.model = genai.GenerativeModel(self.config.judge_model)

    def _score(self, prompt: str, key: str) -> Optional[float]:
        try:
            resp = self.model.generate_content(prompt)
            text = (resp.text or "").strip()
            match = re.search(r"\{.*?\}", text, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                val = data.get(key)
                return float(val) if val is not None else None
            # Fallback: bare numeric answer.
            m = re.search(r"(\d+(?:\.\d+)?)", text)
            return float(m.group(1)) if m else None
        except Exception:
            return None

    def faithfulness(self, answer: str, context_chunks: List[str]) -> float:
        if not answer or not context_chunks:
            return 0.0
        context = "\n\n".join(context_chunks)
        prompt = FAITHFULNESS_PROMPT.format(context=context, answer=answer)
        score = self._score(prompt, "faithfulness")
        if score is None:
            return lexical_faithfulness(answer, context_chunks)
        return max(0.0, min(1.0, score))

    def answer_relevance(self, question: str, answer: str) -> float:
        if not answer:
            return 0.0
        prompt = RELEVANCE_PROMPT.format(question=question, answer=answer)
        score = self._score(prompt, "relevance")
        if score is None:
            return 0.5
        return max(0.0, min(1.0, score))

    def evaluate(self, question: str, answer: str, context_chunks: List[str]) -> dict:
        return {
            "faithfulness": self.faithfulness(answer, context_chunks),
            "answer_relevance": self.answer_relevance(question, answer),
        }