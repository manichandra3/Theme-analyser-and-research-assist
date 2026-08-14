import re
from abc import ABC, abstractmethod
from typing import Callable, List

from .types import Chunk

TOKEN_ESTIMATOR = Callable[[str], int]


def estimate_tokens(text: str) -> int:
    """Fallback token estimate: ~4 characters per token (English heuristic)."""
    return max(1, len(text) // 4)


class Chunker(ABC):
    """Interface for chunking strategies."""

    @abstractmethod
    def chunk(self, doc_id: str, page: int, text: str) -> List[Chunk]:
        ...


class ParagraphChunker(Chunker):
    """Split by paragraph boundaries only (simple baseline)."""

    def __init__(self, tokenizer: TOKEN_ESTIMATOR = estimate_tokens):
        self.tokenizer = tokenizer

    def chunk(self, doc_id: str, page: int, text: str) -> List[Chunk]:
        chunks: List[Chunk] = []
        start = 0
        for num, para in enumerate(text.split("\n\n")):
            para = para.strip()
            if not para:
                continue
            chunks.append(Chunk(
                id=f"{doc_id}_p{page}_c{num}",
                text=para,
                doc_id=doc_id,
                page=page,
                chunk_num=num,
                start_char=start,
                end_char=start + len(para),
                token_count=self.tokenizer(para),
            ))
            start += len(para) + 2
        return chunks


class RecursiveChunker(Chunker):
    """Recursive semantic chunking.

    Splits text on progressively smaller structural separators
    (blank lines, newlines, sentence ends, phrases) then greedily merges
    pieces into fixed-size chunks with configurable token overlap.
    """

    SEPARATORS = ["\n\n", "\n", ". ", "! ", "? ", "; ", ", ", " "]

    def __init__(
        self,
        max_tokens: int = 500,
        overlap_tokens: int = 50,
        tokenizer: TOKEN_ESTIMATOR = estimate_tokens,
    ):
        self.max_tokens = max_tokens
        self.overlap_tokens = min(overlap_tokens, max_tokens // 2)
        self.tokenizer = tokenizer

    def _split_recursive(self, text: str) -> List[str]:
        if self.tokenizer(text) <= self.max_tokens:
            return [text]

        for sep in self.SEPARATORS:
            if sep in text:
                pieces = text.split(sep)
                if len(pieces) > 1:
                    nested = []
                    for piece in pieces:
                        nested.extend(self._split_recursive(piece))
                    return [p for p in nested if p.strip()]

        # No separator worked; hard-cut on whitespace boundaries.
        words = text.split(" ")
        pieces, current = [], []
        for word in words:
            if current and self.tokenizer(" ".join(current)) + self.tokenizer(word) > self.max_tokens:
                pieces.append(" ".join(current))
                current = [word]
            else:
                current.append(word)
        if current:
            pieces.append(" ".join(current))
        return [p for p in pieces if p.strip()]

    def _overlap_tail(self, text: str) -> str:
        words = text.split(" ")
        tail: List[str] = []
        used = 0
        for word in reversed(words):
            if used + self.tokenizer(word) > self.overlap_tokens:
                break
            tail.append(word)
            used += self.tokenizer(word)
        return " ".join(reversed(tail))

    def chunk(self, doc_id: str, page: int, text: str) -> List[Chunk]:
        text = re.sub(r"\s+", " ", text).strip() if not text.strip() else text
        pieces = self._split_recursive(text)

        chunks: List[Chunk] = []
        current: List[str] = []
        current_tokens = 0
        cursor = 0

        for piece in pieces:
            piece_tokens = self.tokenizer(piece)
            if current_tokens + piece_tokens > self.max_tokens and current:
                body = " ".join(current)
                chunks.append(Chunk(
                    id=f"{doc_id}_p{page}_c{len(chunks)}",
                    text=body,
                    doc_id=doc_id,
                    page=page,
                    chunk_num=len(chunks),
                    start_char=cursor,
                    end_char=cursor + len(body),
                    token_count=self.tokenizer(body),
                ))
                tail = self._overlap_tail(body)
                cursor += len(body) - len(tail)
                current = [tail] if tail else []
                current_tokens = self.tokenizer(tail) if tail else 0

            current.append(piece)
            current_tokens += piece_tokens

        if current:
            body = " ".join(current)
            chunks.append(Chunk(
                id=f"{doc_id}_p{page}_c{len(chunks)}",
                text=body,
                doc_id=doc_id,
                page=page,
                chunk_num=len(chunks),
                start_char=cursor,
                end_char=cursor + len(body),
                token_count=self.tokenizer(body),
            ))
        return chunks


def get_chunker(strategy: str, **kwargs) -> Chunker:
    """Factory for chunkers."""
    if strategy == "recursive":
        return RecursiveChunker(**kwargs)
    if strategy == "paragraph":
        return ParagraphChunker()
    raise ValueError(f"Unknown chunking strategy: {strategy}")