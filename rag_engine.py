"""Simple RAG engine for MilkLab° knowledge base."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List
import re

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
        raw_blocks = [chunk.strip() for chunk in re.split(r"\n\s*\n", text) if chunk.strip()]

        # Keep headings with the content below them; also split very large blocks
        chunks: List[str] = []
        for block in raw_blocks:
            if len(block) <= 700:
                chunks.append(block)
                continue

            subparts = [part.strip() for part in block.split("\n") if part.strip()]
            chunks.extend(subparts)

        return chunks

    def _build_index(self):
        embeddings = self.model.encode(self.chunks, show_progress_bar=False)
        matrix = np.array(embeddings, dtype="float32")
        index = faiss.IndexFlatL2(matrix.shape[1])
        index.add(matrix)
        return index

    def search(self, query: str, top_k: int = 3) -> List[str]:
        top_k = max(1, min(top_k, len(self.chunks)))
        query_embedding = self.model.encode([query], show_progress_bar=False)
        query_matrix = np.array(query_embedding, dtype="float32")
        _, indices = self.index.search(query_matrix, top_k)
        results = [self.chunks[i] for i in indices[0] if i >= 0]

        # De-duplicate while preserving order
        seen = set()
        unique_results = []
        for chunk in results:
            if chunk not in seen:
                seen.add(chunk)
                unique_results.append(chunk)
        return unique_results
