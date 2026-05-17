import sys
import json
import pickle
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE))

from semantic.embedding_engine import embedding_engine

with open(BASE / "data" / "role_skill_map_modern.json") as f:
    role_map = json.load(f)

roles = []
texts = []

for role, skills in role_map.items():
    text = role + " " + " ".join(skills)

    roles.append(role)
    texts.append(text)

print("Encoding roles...")

embeddings = embedding_engine.encode(texts)

data = {
    "roles": roles,
    "embeddings": embeddings
}

with open(BASE / "data" / "role_embeddings.pkl", "wb") as f:
    pickle.dump(data, f)

print("Saved role embeddings:", len(roles))