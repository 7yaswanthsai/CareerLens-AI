"""
matching/matcher.py  —  Fixed scoring: all scores in [0, 100]
semantic_sim(0-1)*0.50 + skill_ratio(0-1)*0.35 + log_density(0-1)*0.15
"""
from __future__ import annotations
import math, torch
from semantic.embedding_engine import embedding_engine
from resume_processing.skills import extract_skills_from_text

_ec: dict = {}
_sc: dict = {}

def _emb(text):
    k = text[:500]
    if k not in _ec: _ec[k] = embedding_engine.encode(text)[0]
    return _ec[k]

def _skills(text):
    k = text[:500]
    if k not in _sc: _sc[k] = extract_skills_from_text(text)
    return _sc[k]

def rank_jobs_by_similarity(resume_text: str, jobs: list) -> list:
    re_emb = _emb(resume_text)
    re_sk  = _skills(resume_text)
    r_set  = {s.lower() for s in re_sk}
    ranked = []
    for job in jobs:
        desc = job.get("description","")
        if not desc: continue
        je    = _emb(desc)
        sem   = (torch.dot(re_emb, je).item() + 1.0) / 2.0   # [-1,1] -> [0,1]
        j_set = {s.lower() for s in _skills(desc)}
        ovlp  = len(r_set & j_set)
        ratio = ovlp / max(len(j_set), 1)
        dens  = min(math.log2(1 + ovlp) / math.log2(16), 1.0)
        score = sem*0.50 + ratio*0.35 + dens*0.15
        job["match_score"] = round(min(score*100, 100.0), 1)
        ranked.append(job)
    ranked.sort(key=lambda x: x["match_score"], reverse=True)
    return ranked