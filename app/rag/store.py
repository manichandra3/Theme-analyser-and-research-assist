from typing import Dict, List, Optional

import chromadb
from chromadb.config import Settings

from .retrieval import VectorStoreAdapter, cosine
from .types import Chunk, RetrievedChunk


class ChromaAdapter(VectorStoreAdapter):
    """VectorStoreAdapter backed by a Chroma collection.

    Chunks are stored as Chroma documents with an id of
    ``<doc_id>_p<page>_c<chunk_num>`` and metadata carrying doc_id/page so
    deletes and provenance lookups stay simple.
    """

    def __init__(self, persist_dir: str = "data/chroma",
                 collection_name: str = "documents"):
        self.client = chromadb.Client(Settings(
            persist_directory=persist_dir,
            anonymized_telemetry=False,
        ))
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def all_chunks(self) -> Dict[str, Chunk]:
        data = self.collection.get(include=["documents", "metadatas"])
        chunks: Dict[str, Chunk] = {}
        ids = data.get("ids") or []
        docs = data.get("documents") or []
        metas = data.get("metadatas") or []
        for i, cid in enumerate(ids):
            meta = metas[i] if i < len(metas) else {}
            chunks[cid] = Chunk(
                id=cid,
                text=docs[i] if i < len(docs) else "",
                doc_id=str(meta.get("doc_id", "")),
                page=int(meta.get("page", 0) or 0),
                chunk_num=int(meta.get("chunk_num", 0) or 0),
                metadata=dict(meta),
            )
        return chunks

    def dense_search(self, query_embedding: List[float], k: int) -> List[RetrievedChunk]:
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            include=["documents", "metadatas", "distances"],
        )
        out: List[RetrievedChunk] = []
        docs = (results.get("documents") or [[]])[0]
        metas = (results.get("metadatas") or [[]])[0]
        dists = (results.get("distances") or [[]])[0]
        ids = (results.get("ids") or [[]])[0]
        for i, cid in enumerate(ids):
            meta = metas[i] if i < len(metas) else {}
            score = dists[i] if i < len(dists) else 0.0
            out.append(RetrievedChunk(
                chunk=Chunk(
                    id=cid,
                    text=docs[i] if i < len(docs) else "",
                    doc_id=str(meta.get("doc_id", "")),
                    page=int(meta.get("page", 0) or 0),
                    chunk_num=int(meta.get("chunk_num", 0) or 0),
                    metadata=dict(meta),
                ),
                dense_score=1.0 - score,  # chroma distance -> similarity
            ))
        return out

    def add_chunks(self, chunks: List[Chunk], embeddings: List[List[float]]) -> None:
        self.collection.add(
            ids=[c.id for c in chunks],
            embeddings=embeddings,
            documents=[c.text for c in chunks],
            metadatas=[
                {
                    "doc_id": c.doc_id,
                    "page": c.page,
                    "chunk_num": c.chunk_num,
                    "paragraph": c.chunk_num,  # legacy field the frontend reads
                    "tokens": c.token_count,
                }
                for c in chunks
            ],
        )

    def delete_doc(self, doc_id: str) -> None:
        ids = [c.id for c in self.all_chunks().values() if c.doc_id == doc_id]
        if ids:
            self.collection.delete(ids=ids)

    def clear(self) -> None:
        ids = self.all_chunks().keys()
        if ids:
            self.collection.delete(ids=list(ids))