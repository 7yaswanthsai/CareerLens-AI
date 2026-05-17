from collections import Counter
import torch
from semantic.embedding_engine import embedding_engine
from analysis.skill_gap import extract_phrases


def build_market_heatmap(jobs, top_n=20):

    all_phrases = []

    for job in jobs:
        desc = job.get("description", "")
        phrases = extract_phrases(desc)
        all_phrases.extend(phrases[:10])  # limit per job for performance

    if not all_phrases:
        return []

    embeddings = embedding_engine.encode(all_phrases)
    embeddings = torch.stack(embeddings)

    # Simple similarity-based grouping
    clusters = []
    used = set()

    for i in range(len(all_phrases)):
        if i in used:
            continue

        cluster = [all_phrases[i]]
        used.add(i)

        for j in range(i+1, len(all_phrases)):
            if j in used:
                continue

            sim = torch.dot(embeddings[i], embeddings[j]).item()

            if sim > 0.75:
                cluster.append(all_phrases[j])
                used.add(j)

        clusters.append(cluster)

    cluster_counts = [(cluster[0], len(cluster)) for cluster in clusters]
    cluster_counts.sort(key=lambda x: x[1], reverse=True)

    return cluster_counts[:top_n]