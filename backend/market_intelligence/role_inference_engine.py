import json
import torch
from semantic.embedding_engine import embedding_engine

with open("data/role_prototypes.json", "r", encoding="utf-8") as f:
    role_data = json.load(f)

roles = [r["role"] for r in role_data]
role_texts = [r["role"] + " " + r["description"] for r in role_data]

print("Loading role prototype embeddings...")

role_embeddings = embedding_engine.encode(role_texts)


def infer_roles_from_resume(resume_text, top_k=5):

    resume_embedding = embedding_engine.encode(resume_text)[0]

    scores = []

    for i, role_embedding in enumerate(role_embeddings):
        similarity = torch.dot(resume_embedding, role_embedding).item()
        scores.append((roles[i], similarity))

    scores.sort(key=lambda x: x[1], reverse=True)

    return [r[0] for r in scores[:top_k]]