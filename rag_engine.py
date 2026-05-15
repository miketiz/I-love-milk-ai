"""Simple RAG engine for MilkLab° knowledge base."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


@dataclass
class SearchResult:
    chunk: str
    score: float


class RAGEngine:
    def __init__(self, kb_path: str):
        self.kb_path = Path(kb_path)
        self.model = SentenceTransformer(EMBED_MODEL)
        self.chunks = self._load_and_chunk(self.kb_path)
        self.index = self._build_index()

    def _load_and_chunk(self, path: Path) -> List[str]:
        text = path.read_text(encoding="utf-8")
        chunks = [chunk.strip() for chunk in text.split("\n\n") if chunk.strip()]
        return chunks

    def _build_index(self):
        embeddings = self.model.encode(self.chunks, show_progress_bar=False)
        matrix = np.array(embeddings, dtype="float32")
        index = faiss.IndexFlatL2(matrix.shape[1])
        index.add(matrix)
        return index

    def search(self, query: str, top_k: int = 3) -> List[str]:
        query_embedding = self.model.encode([query], show_progress_bar=False)
        query_matrix = np.array(query_embedding, dtype="float32")
        _, indices = self.index.search(query_matrix, top_k)
        return [self.chunks[i] for i in indices[0] if i >= 0]
