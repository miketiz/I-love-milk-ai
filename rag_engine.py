from dataclasses import dataclass
from pathlib import Path
from typing import List
import re
import hashlib

import faiss
import numpy as np

EMBED_DIM = 384

try:
    from sentence_transformers import SentenceTransformer
except Exception:
    SentenceTransformer = None

EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


class _FallbackSentenceTransformer:
    """Lightweight embedder used when sentence-transformers cannot be imported."""

    def __init__(self, dimension: int = EMBED_DIM):
        self.dimension = dimension

    def encode(self, texts, show_progress_bar: bool = False):
        if isinstance(texts, str):
            texts = [texts]

        matrix = np.zeros((len(texts), self.dimension), dtype=np.float32)
        for row_index, text in enumerate(texts):
            for token in re.findall(r"\w+", text.lower()):
                token_hash = hashlib.md5(token.encode("utf-8")).hexdigest()
                column_index = int(token_hash, 16) % self.dimension
                matrix[row_index, column_index] += 1.0

        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return matrix / norms


@dataclass
class SearchResult:
    chunk: str
    score: float


class RAGEngine:
    def __init__(self, kb_path: str):
        self.kb_path = Path(kb_path)
        self.model = self._create_model()
        self.chunks = self._load_and_chunk(self.kb_path)
        self.index = self._build_index()

    def _create_model(self):
        if SentenceTransformer is None:
            return _FallbackSentenceTransformer()

        try:
            return SentenceTransformer(EMBED_MODEL)
        except Exception:
            return _FallbackSentenceTransformer()

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

    def search_with_scores(self, query: str, top_k: int = 3) -> List[SearchResult]:
        top_k = max(1, min(top_k, len(self.chunks)))

        normalized_query = re.sub(r"\s+", " ", query.strip().lower())
        exact_matches = []
        for chunk in self.chunks:
            normalized_chunk = re.sub(r"\s+", " ", chunk.strip().lower())
            if normalized_query and (
                normalized_query in normalized_chunk or normalized_chunk in normalized_query
            ):
                exact_matches.append(SearchResult(chunk=chunk, score=0.0))

        if exact_matches:
            seen_exact = set()
            deduped_exact = []
            for result in exact_matches:
                if result.chunk in seen_exact:
                    continue
                seen_exact.add(result.chunk)
                deduped_exact.append(result)
            return deduped_exact[:top_k]

        query_embedding = self.model.encode([query], show_progress_bar=False)
        query_matrix = np.array(query_embedding, dtype="float32")
        distances, indices = self.index.search(query_matrix, top_k)

        results: List[SearchResult] = []
        seen = set()
        for distance, index in zip(distances[0], indices[0]):
            if index < 0:
                continue

            chunk = self.chunks[index]
            if chunk in seen:
                continue

            seen.add(chunk)
            results.append(SearchResult(chunk=chunk, score=float(distance)))

        return results

    def search(self, query: str, top_k: int = 3) -> List[str]:
        return [result.chunk for result in self.search_with_scores(query, top_k=top_k)]
