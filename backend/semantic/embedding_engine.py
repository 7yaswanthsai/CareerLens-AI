"""semantic/embedding_engine.py  —  Cached sentence embedding engine"""
from __future__ import annotations
import hashlib
from sentence_transformers import SentenceTransformer

class EmbeddingEngine:
    def __init__(self):
        print("Loading embedding model…")
        self.model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        self._cache: dict = {}

    def _key(self, text: str) -> str:
        return hashlib.md5(text.encode("utf-8")).hexdigest()

    def encode(self, texts):
        if isinstance(texts, str): texts = [texts]
        embeddings, to_encode, indices = [], [], []
        for i, t in enumerate(texts):
            k = self._key(t)
            if k in self._cache: embeddings.append(self._cache[k])
            else:
                embeddings.append(None); to_encode.append(t); indices.append(i)
        if to_encode:
            new_embs = self.model.encode(to_encode, convert_to_tensor=True,
                                         normalize_embeddings=True, batch_size=32)
            for i, emb in enumerate(new_embs):
                orig = indices[i]
                self._cache[self._key(texts[orig])] = emb
                embeddings[orig] = emb
        return embeddings if len(embeddings) > 1 else [embeddings[0]]

embedding_engine = EmbeddingEngine()