import math
import re
from collections import Counter
from typing import Dict, List, Set, Tuple

STOPWORDS: Set[str] = {
    "a", "an", "the", "and", "or", "but", "if", "then", "else", "for", "of", "on",
    "in", "to", "at", "by", "with", "from", "as", "is", "are", "was", "were", "be",
    "been", "being", "it", "its", "this", "that", "these", "those", "i", "you",
    "he", "she", "we", "they", "not", "no", "so", "do", "does", "did", "have",
    "has", "had", "will", "would", "can", "could", "should", "may", "might",
}

TOKEN_RE = re.compile(r"[a-zA-Z0-9]+(?:['-][a-zA-Z0-9]+)*")


def tokenize(text: str) -> List[str]:
    """Lowercase tokenization with stopword removal (no external deps)."""
    return [t.lower() for t in TOKEN_RE.findall(text) if t.lower() not in STOPWORDS]


def build_terms(text: str) -> Counter:
    return Counter(tokenize(text))


class BM25Index:
    """Pure-Python best-match-25 sparse index over chunk texts.

    Uses Okapi BM25 with k1/b smoothing. Keeps a mapping from chunk id to
    index position so sparse results can be merged with dense results via RRF.
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.ids: List[str] = []
        self._doc_terms: List[Counter] = []
        self._doc_len: List[int] = []
        self._avgdl: float = 0.0
        self._idf: Dict[str, float] = {}
        self._built = False

    def build(self, id_texts: Dict[str, str]) -> None:
        """Build index from a mapping of chunk_id -> text."""
        self.ids = list(id_texts.keys())
        self._doc_terms = [build_terms(t) for t in id_texts.values()]
        self._doc_len = [sum(t.values()) for t in self._doc_terms]
        self._avgdl = sum(self._doc_len) / max(1, len(self._doc_len))

        df: Counter = Counter()
        for terms in self._doc_terms:
            df.update(terms.keys())
        n_docs = len(self._doc_terms)
        self._idf = {
            term: math.log(1 + (n_docs - freq + 0.5) / (freq + 0.5))
            for term, freq in df.items()
        }
        self._built = True

    def search(self, query: str, top_k: int = 20) -> List[Tuple[str, float]]:
        """Return top_k (chunk_id, score) pairs sorted by relevance."""
        if not self._built:
            return []
        query_terms = build_terms(query)
        if not query_terms:
            return []
        scored = []
        for idx, doc_len in enumerate(self._doc_len):
            if doc_len == 0:
                continue
            score = 0.0
            for term, qf in query_terms.items():
                tf = self._doc_terms[idx].get(term, 0)
                idf = self._idf.get(term, 0.0)
                if tf == 0 or idf == 0:
                    continue
                denom = tf + self.k1 * (1 - self.b + self.b * doc_len / self._avgdl) + 1e-9
                score += qf * idf * (tf * (self.k1 + 1)) / denom
            if score > 0:
                scored.append((self.ids[idx], score))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]