"""Simple RAG engine for MilkLab° knowledge base."""

from __future__ import annotations

# ⚠️ CRITICAL: Block torch imports BEFORE sentence-transformers import
# This prevents: ValueError: torch.__spec__ is None
import sys
import types
import importlib.util


def _block_torch():
    """Pre-create dummy torch modules."""
    def _create_dummy(name):
        mod = types.ModuleType(name)
        # Create a proper spec instead of None to avoid ValueError
        mod.__spec__ = importlib.util.spec_from_loader(name, loader=None)
        mod.__loader__ = None
        return mod

    torch_mod = _create_dummy('torch')
    # Add stub tensor types and common attributes that transformers expects
    torch_mod.LongTensor = type('LongTensor', (), {})
    torch_mod.FloatTensor = type('FloatTensor', (), {})
    torch_mod.Tensor = type('Tensor', (), {})
    torch_mod.device = type('device', (), {})
    torch_mod.cuda = _create_dummy('torch.cuda')
    torch_mod.cuda.is_available = lambda: False
    torch_mod.cuda.device_count = lambda: 0
    torch_mod.distributed = _create_dummy('torch.distributed')
    torch_mod.multiprocessing = _create_dummy('torch.multiprocessing')
    torch_mod.nn = _create_dummy('torch.nn')
    torch_mod.nn.Module = type('Module', (), {})
    torch_mod.nn.Parameter = type('Parameter', (), {})
    torch_mod.optim = _create_dummy('torch.optim')
    sys.modules['torch'] = torch_mod
    sys.modules['torch.cuda'] = torch_mod.cuda
    sys.modules['torch.distributed'] = torch_mod.distributed
    sys.modules['torch.multiprocessing'] = torch_mod.multiprocessing
    sys.modules['torch.nn'] = torch_mod.nn
    sys.modules['torch.optim'] = torch_mod.optim
    
    tv = _create_dummy('torchvision')
    tv.transforms = _create_dummy('torchvision.transforms')
    tv.transforms.v2 = _create_dummy('torchvision.transforms.v2')
    tv.transforms.v2.functional = _create_dummy('torchvision.transforms.v2.functional')
    tv.io = _create_dummy('torchvision.io')
    tv.ops = _create_dummy('torchvision.ops')
    tv.ops.boxes = _create_dummy('torchvision.ops.boxes')
    
    sys.modules['torchvision'] = tv
    sys.modules['torchvision.transforms'] = tv.transforms
    sys.modules['torchvision.transforms.v2'] = tv.transforms.v2
    sys.modules['torchvision.transforms.v2.functional'] = tv.transforms.v2.functional
    sys.modules['torchvision.io'] = tv.io
    sys.modules['torchvision.ops'] = tv.ops
    sys.modules['torchvision.ops.boxes'] = tv.ops.boxes


_block_torch()

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

    def search_with_scores(self, query: str, top_k: int = 3) -> List[SearchResult]:
        top_k = max(1, min(top_k, len(self.chunks)))
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
