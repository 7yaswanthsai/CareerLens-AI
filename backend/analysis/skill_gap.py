"""
analysis/skill_gap.py  —  Production skill gap analyzer
Synonym-aware: sklearn ↔ scikit-learn, postgres ↔ postgresql, etc.
Filters generic noise from gap lists.
"""
from __future__ import annotations
from resume_processing.skills import extract_skills_from_text, GENERIC

_SYNONYMS = [
    {"scikit-learn","sklearn"}, {"pytorch","torch"}, {"tensorflow","keras"},
    {"postgresql","postgres","psql"}, {"mongodb","mongo"},
    {"rest api","restful api","restful apis","rest apis"},
    {"machine learning","ml"}, {"deep learning","dl"},
    {"natural language processing","nlp"}, {"computer vision","cv"},
    {"large language models","llm","llms"}, {"ci/cd","cicd"},
    {"object oriented programming","oop"}, {"aws","amazon web services"},
    {"gcp","google cloud","google cloud platform"}, {"azure","microsoft azure"},
    {"power bi","powerbi"}, {"kubernetes","k8s"}, {"huggingface","hugging face"},
]

_NOISE = GENERIC | {"programming","scripting","version control","source control",
                    "problem solving","teamwork","communication","agile","scrum"}

def _expand(skill_set):
    exp = set(skill_set)
    for grp in _SYNONYMS:
        if skill_set & grp: exp |= grp
    return exp

def analyze_skill_gap(resume_text: str, job_desc: str) -> dict:
    r_skills = set(s.lower() for s in extract_skills_from_text(resume_text))
    j_skills = set(s.lower() for s in extract_skills_from_text(job_desc))
    j_skills = {s for s in j_skills if s not in _NOISE and len(s) >= 3}
    if not j_skills:
        return {"strong_match": sorted(r_skills)[:8], "partial_match": [], "missing": []}
    r_exp = _expand(r_skills)
    strong  = sorted(r_skills & j_skills)
    partial = sorted((r_exp - r_skills) & j_skills)
    missing = sorted(j_skills - r_exp - r_skills)
    missing = [s for s in missing if s not in _NOISE and len(s) >= 3]
    return {"strong_match": strong[:8], "partial_match": partial[:4], "missing": missing[:8]}