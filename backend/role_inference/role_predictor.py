"""
role_inference/role_predictor.py  —  Production role predictor
3-tier: embedding similarity → skill-cluster scoring → keyword heuristic
Experience level injected so Fresher gets junior roles, not principal roles.
"""
from __future__ import annotations
import json, pickle, re
from pathlib import Path
from collections import Counter

_BASE = Path(__file__).resolve().parents[1]

try:
    from semantic.embedding_engine import embedding_engine as _emb; _HAS_EMB = True
except Exception: _HAS_EMB = False
try:
    from sklearn.metrics.pairwise import cosine_similarity as _cos
    import numpy as np; _HAS_SK = True
except ImportError: _HAS_SK = False

_ROLES, _ROLE_EMB = [], None
try:
    with open(_BASE/"data"/"role_embeddings.pkl","rb") as f: _d = pickle.load(f)
    _ROLES, _ROLE_EMB = _d["roles"], _d["embeddings"]
except Exception: pass

# Skill clusters → (role_title, min_overlap)
_CLUSTERS = [
    ({"machine learning","pandas","scikit-learn","statistics","python","numpy"},    "Data Scientist",         3),
    ({"pytorch","tensorflow","deep learning","neural networks","model training"},    "Machine Learning Engineer",2),
    ({"natural language processing","transformers","bert","spacy","nltk"},           "NLP Engineer",           2),
    ({"computer vision","opencv","image classification","object detection","yolo"},  "Computer Vision Engineer",2),
    ({"mlflow","airflow","model deployment","mlops","sagemaker","kubeflow"},         "MLOps Engineer",         2),
    ({"large language models","langchain","rag pipeline","faiss","huggingface"},     "LLM / GenAI Engineer",   2),
    ({"power bi","tableau","sql","excel","data visualization"},                      "Data Analyst",           3),
    ({"pyspark","kafka","dbt","data pipeline","bigquery","etl"},                     "Data Engineer",          2),
    ({"sql","postgresql","database design","query optimization"},                    "Database Developer",     2),
    ({"react","javascript","typescript","html","css"},                               "Frontend Developer",     3),
    ({"fastapi","flask","django","rest api","node.js"},                              "Backend Developer",      2),
    ({"docker","kubernetes","terraform","ci/cd","aws","linux"},                      "DevOps Engineer",        3),
    ({"aws","azure","gcp","cloud","terraform"},                                      "Cloud Engineer",         2),
    ({"java","spring","microservices","sql"},                                        "Java Developer",         2),
    ({"python","django","flask","rest api"},                                         "Python Developer",       3),
    ({"figma","user research","wireframing","prototyping"},                          "UX Designer",            2),
    ({"penetration testing","security audits","ethical hacking"},                   "Security Engineer",      2),
    ({"kotlin","android","android sdk"},                                             "Android Developer",      2),
    ({"swift","ios","xcode"},                                                        "iOS Developer",          2),
    ({"react native","flutter","mobile app development"},                            "Mobile Developer",       2),
    ({"power bi","dax","data modeling","business intelligence"},                     "Power BI Developer",     2),
    ({"agile","product roadmap","stakeholder management","user research"},           "Product Manager",        2),
]

_LEVEL_CTX = {
    "Fresher":   "entry level fresher graduate internship junior",
    "Junior":    "junior associate entry level 1 year",
    "Mid-Level": "mid level 3 years professional",
    "Senior":    "senior lead principal 7 years",
}
_BAD = {"datadog","splunk","snowflake","gerrit","bamboo","jenkins","artifactory",
        "teamcity","jira","confluence","zabbix","nagios","sonarqube","nexus"}

def _clean(r):
    if any(w in r.lower() for w in _BAD) or len(r.split()) > 6: return None
    return r.strip()

def _dedup(roles, k):
    seen, out = set(), []
    for r in roles:
        words = set(r.lower().split())
        if len(words & seen) < 2: out.append(r); seen |= words
        if len(out) >= k: break
    return out

def predict_roles(resume_text: str, resume_skills: list, level: str = "Mid-Level", top_k: int = 5) -> list:
    skill_set = {s.lower() for s in resume_skills}

    # Tier 1: embeddings
    if _HAS_EMB and _HAS_SK and _ROLE_EMB is not None:
        try:
            ctx   = _LEVEL_CTX.get(level, "")
            query = resume_text[:2000] + " " + " ".join(resume_skills) + " " + ctx
            q_emb = _emb.encode([query])
            rm = _ROLE_EMB.numpy() if hasattr(_ROLE_EMB,"numpy") else np.array(_ROLE_EMB)
            qa = q_emb[0].numpy().reshape(1,-1) if hasattr(q_emb[0],"numpy") else np.array(q_emb[0]).reshape(1,-1)
            scores = _cos(qa, rm)[0]
            ranked = sorted(zip(_ROLES, scores), key=lambda x: x[1], reverse=True)
            cands  = [_clean(r).title() for r,_ in ranked if _clean(r)][:top_k*3]
            result = _dedup(cands, top_k)
            if len(result) >= 3: return result
        except Exception: pass

    # Tier 2: skill clusters
    counter = Counter()
    for skill_set_ref, title, min_n in _CLUSTERS:
        overlap = len(frozenset(skill_set_ref) & skill_set)
        if overlap >= min_n: counter[title] += overlap / len(skill_set_ref)
    if counter:
        result = _dedup([r for r,_ in counter.most_common(top_k*2)], top_k)
        if result: return result

    # Tier 3: keyword heuristic
    for sig, role in [("machine learning","Data Scientist"),("pytorch","Machine Learning Engineer"),
                      ("python","Python Developer"),("react","Frontend Developer"),
                      ("docker","DevOps Engineer"),("figma","UX Designer"),("sql","Data Analyst")]:
        if sig in skill_set: return [role]
    return ["Software Engineer"]