"""market_intelligence/clustering.py  —  Discover roles from job listings"""
from __future__ import annotations
from collections import Counter

def discover_roles_from_jobs(jobs: list, k: int = 5) -> list:
    texts = [j.get("title","") for j in jobs if j.get("title","").strip()]
    if not texts: return []
    try:
        from semantic.embedding_engine import embedding_engine
        from sklearn.cluster import KMeans
        import numpy as np
        embs = embedding_engine.encode(texts)
        k = min(k, len(texts))
        matrix = np.array([e.numpy() if hasattr(e,"numpy") else e for e in embs])
        labels = KMeans(n_clusters=k, random_state=42, n_init=10).fit_predict(matrix)
        clusters = {}
        for i, lbl in enumerate(labels):
            clusters.setdefault(lbl, []).append(texts[i])
        return [Counter(v).most_common(1)[0][0] for v in clusters.values()]
    except Exception:
        # Simple fallback: most common titles
        return [t for t,_ in Counter(texts).most_common(k)]