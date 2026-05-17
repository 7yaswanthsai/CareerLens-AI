"""
resume_processing/skills.py  —  Production skill extractor
• 6700+ term vocabulary (ESCO + Kaggle + hand-curated)
• Alias normalisation, 1/2/3-gram matching, noise blocklist
"""
from __future__ import annotations
import re, json
from pathlib import Path
from functools import lru_cache

_DATA = Path(__file__).resolve().parents[1] / "data"

@lru_cache(maxsize=1)
def _vocab() -> frozenset:
    for name in ("skills_master.json","skills_vocabulary_enhanced.json","skills_vocabulary_modern.json"):
        p = _DATA / name
        if p.exists():
            with open(p, encoding="utf-8") as f:
                raw = json.load(f)
            return frozenset(s.lower().strip() for s in raw if isinstance(s,str) and s.strip())
    return frozenset()

ALIASES = {
    "scikit learn":"scikit-learn","sci-kit learn":"scikit-learn","sklearn":"scikit-learn",
    "torch":"pytorch","cv2":"opencv","open cv":"opencv",
    "amazon web services":"aws","google cloud platform":"gcp",
    "microsoft azure":"azure","azure cloud":"azure",
    "powerbi":"power bi","ms power bi":"power bi",
    "ms excel":"excel","microsoft excel":"excel",
    "postgres":"postgresql","psql":"postgresql",
    "mongo":"mongodb","mongo db":"mongodb",
    "mssql":"sql server","microsoft sql server":"sql server",
    "elastic search":"elasticsearch","k8s":"kubernetes",
    "nlp":"natural language processing","cv":"computer vision",
    "ml":"machine learning","dl":"deep learning",
    "ai":"artificial intelligence",
    "llm":"large language models","llms":"large language models",
    "rag":"rag pipeline","eda":"exploratory data analysis",
    "cnn":"convolutional neural networks","rnn":"recurrent neural networks",
    "rest apis":"rest api","restful api":"rest api","restful apis":"rest api","restful":"rest api",
    "cicd":"ci/cd","ci cd":"ci/cd",
    "oop":"object oriented programming","object-oriented programming":"object oriented programming",
    "hugging face":"huggingface","git/github":"git",
    "fe":None,"hf":None,"pd":None,"np":None,"plt":None,"sns":None,
}

GENERIC = frozenset({
    "analysis","analytics","approach","architecture","assessment","benchmarking",
    "capability","collaboration","communication","concept","concepts","coordination",
    "creation","decision","decisions","delivery","design","development","documentation",
    "efficiency","evaluation","execution","experiments","expertise","framework","frameworks",
    "functionality","implementation","improvement","improvements","innovation","integration",
    "knowledge","leadership","learning","logic","management","method","methodology",
    "model","models","monitoring","operations","optimization","performance","pipeline",
    "planning","process","processes","productivity","program","programs","project",
    "projects","quality","research","reporting","results","review","scalability","scaling",
    "solution","solutions","strategy","strategies","structures","support","system","systems",
    "tasks","technique","techniques","testing","training","troubleshooting","understanding",
    "validation","workflow","workflows","computer science","dashboards","databases",
    "performance monitoring","orchestration","sign language","programming","scripting",
    "coding","software","technology","data","engineering","science","development","deployment",
})

_TOKEN = re.compile(r"[a-zA-Z][a-zA-Z0-9+#\./\-]*")

def extract_skills_from_text(text: str) -> list:
    vocab = _vocab()
    tl    = text.lower()
    found = set()
    for alias, canonical in ALIASES.items():
        if canonical and re.search(r"\b" + re.escape(alias) + r"\b", tl):
            if canonical not in GENERIC and len(canonical) >= 3:
                found.add(canonical)
    words = _TOKEN.findall(tl)
    for i in range(len(words)):
        for w in range(1, 4):
            if i + w > len(words): break
            phrase = " ".join(words[i:i+w])
            if phrase in vocab and phrase not in GENERIC and len(phrase) >= 3:
                found.add(phrase)
    return sorted(s for s in found if s not in GENERIC and len(s) >= 3)