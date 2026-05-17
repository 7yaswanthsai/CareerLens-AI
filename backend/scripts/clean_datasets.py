import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

esco_skills = json.load(open(BASE_DIR / "data" / "skills_vocabulary_clean.json"))
modern_skills = json.load(open(BASE_DIR / "data" / "skills_vocabulary_modern.json"))

final_skills = set()

for s in esco_skills:
    if len(s) > 2:
        final_skills.add(s.lower())

for s in modern_skills:
    final_skills.add(s.lower())

with open(BASE_DIR / "data" / "skills_vocabulary_final.json", "w") as f:
    json.dump(sorted(list(final_skills)), f, indent=2)

print("Final Skills:", len(final_skills))