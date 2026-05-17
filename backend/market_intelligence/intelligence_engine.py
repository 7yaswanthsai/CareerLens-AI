"""
market_intelligence/intelligence_engine.py  —  Production intelligence engine

Fixes:
• market_strength_score uses actual embedding-based job matching (0-1)
• missing_high_impact_skills correctly compares resume vs market (not self)
• roi_simulation uses normalized scores so improvement_percent makes sense
• No duplicate imports, no dead code
"""
from __future__ import annotations
import asyncio
from collections import Counter
from resume_processing.skills import extract_skills_from_text
from market_intelligence.clustering import discover_roles_from_jobs
from matching.matcher import rank_jobs_by_similarity

# ── Market skill frequency heatmap ────────────────────────────────────────────
def build_market_heatmap(jobs: list, top_n: int = 10) -> list:
    """Count skill frequency across all job descriptions."""
    counter: Counter = Counter()
    for job in jobs:
        desc = job.get("description","")
        if desc:
            for skill in extract_skills_from_text(desc):
                counter[skill] += 1
    return counter.most_common(top_n)


# ── Market strength score (0.0 – 1.0) ────────────────────────────────────────
def calculate_market_strength(resume_text: str, jobs: list) -> float:
    """Average normalised match score across top-20 jobs."""
    ranked = rank_jobs_by_similarity(resume_text, jobs)
    if not ranked: return 0.0
    avg = sum(j["match_score"] for j in ranked[:20]) / min(20, len(ranked))
    return round(avg / 100.0, 2)


# ── Missing high-impact skills ────────────────────────────────────────────────
def find_missing_skills(resume_skills: list, heatmap: list) -> list:
    """Skills in the market heatmap that the resume does NOT have."""
    r_set = {s.lower() for s in resume_skills}
    missing = []
    for skill, freq in heatmap:
        if skill.lower() not in r_set:
            missing.append({"skill": skill, "market_frequency": freq})
    return missing[:5]


# ── ROI simulation ────────────────────────────────────────────────────────────
def simulate_roi(resume_text: str, jobs: list, missing_skills: list) -> list:
    """Simulate match-score improvement if each missing skill is added."""
    base = rank_jobs_by_similarity(resume_text, jobs)
    if not base: return []
    base_avg = sum(j["match_score"] for j in base[:20]) / max(1, min(20, len(base)))
    results  = []
    for item in missing_skills[:3]:
        sk   = item["skill"]
        mod  = rank_jobs_by_similarity(resume_text + " " + sk, jobs)
        if not mod: continue
        new_avg = sum(j["match_score"] for j in mod[:20]) / max(1, min(20, len(mod)))
        results.append({"skill": sk, "improvement_percent": round(new_avg - base_avg, 2)})
    return results


# ── Main entry point ──────────────────────────────────────────────────────────
async def generate_career_summary(
    resume_text: str,
    resume_skills: list,
    roles: list,
    jobs: list,
) -> dict:
    heatmap       = build_market_heatmap(jobs, top_n=10)
    strength      = calculate_market_strength(resume_text, jobs)
    missing       = find_missing_skills(resume_skills, heatmap)
    roi           = simulate_roi(resume_text, jobs, missing)
    discovered    = discover_roles_from_jobs(jobs)

    return {
        "top_roles":                roles,
        "market_strength_score":    strength,
        "top_market_skills":        heatmap,
        "missing_high_impact_skills": missing,
        "roi_simulation":           roi,
        "discovered_roles":         discovered,
    }