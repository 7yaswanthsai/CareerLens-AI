"""
ai_features/llm_engine.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LLM engine powering all 7 AI career features.

Provider chain (only 2 — no other APIs needed):
  1. Groq  — Meta Llama 3.3-70B on LPU hardware
             Free: 14 400 req/day · ~600 tok/s
             Get key at: https://console.groq.com
  2. Local — google/flan-t5-base (CPU, zero API)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
from __future__ import annotations
import os, json, re, time, logging
import httpx

log = logging.getLogger(__name__)

_GROQ_MODEL = "llama-3.3-70b-versatile"
_GROQ_KEY   = os.environ.get("GROQ_API_KEY", "")

_local_tok   = None
_local_model = None


# ── Provider 1: Groq ──────────────────────────────────────────────────────────
def _call_groq(system: str, user: str, max_tokens: int) -> str:
    if not _GROQ_KEY:
        raise RuntimeError("GROQ_API_KEY not set in backend/.env")
    r = httpx.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {_GROQ_KEY}", "Content-Type": "application/json"},
        json={
            "model": _GROQ_MODEL,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user",   "content": user},
            ],
            "max_tokens":  max_tokens,
            "temperature": 0.3,
        },
        timeout=45,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip()


# ── Provider 2: Local flan-t5-base ────────────────────────────────────────────
def _load_local():
    global _local_tok, _local_model
    if _local_model is None:
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
        log.info("Loading local flan-t5-base (first run ~30s)...")
        _local_tok   = AutoTokenizer.from_pretrained("google/flan-t5-base")
        _local_model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-base")
        _local_model.eval()


def _call_local(system: str, user: str, max_tokens: int) -> str:
    import torch
    _load_local()
    prompt = f"{system}\n\n{user}"
    inputs = _local_tok(prompt, return_tensors="pt", truncation=True, max_length=1024)
    with torch.no_grad():
        out = _local_model.generate(**inputs, max_new_tokens=min(max_tokens, 512))
    return _local_tok.decode(out[0], skip_special_tokens=True).strip()


# ── Dispatcher ────────────────────────────────────────────────────────────────
_PROVIDERS = [
    ("Groq — Llama 3.3-70B", _call_groq),
    ("Local — flan-t5-base",  _call_local),
]


def _call(system: str, user: str, max_tokens: int = 1200) -> tuple[str, str]:
    errors = []
    for name, fn in _PROVIDERS:
        try:
            result = fn(system, user, max_tokens)
            if result and len(result) > 5:
                return result, name
        except Exception as e:
            log.warning(f"[{name}] failed: {e}")
            errors.append(f"{name}: {e}")
            time.sleep(0.2)
    raise RuntimeError(
        "All LLM providers failed:\n" + "\n".join(errors) +
        "\n\nFix: add GROQ_API_KEY to backend/.env — free at https://console.groq.com"
    )


def _used_provider() -> str:
    return "Groq — Llama 3.3-70B" if _GROQ_KEY else "Local — flan-t5-base"


def _parse_json(raw: str) -> dict | list:
    raw = re.sub(r"^```(?:json)?\s*", "", raw.strip(), flags=re.M)
    raw = re.sub(r"```\s*$",          "", raw.strip(), flags=re.M)
    raw = raw.strip()
    for s_ch, e_ch in [('{', '}'), ('[', ']')]:
        s = raw.find(s_ch)
        if s == -1:
            continue
        depth = 0
        for i, ch in enumerate(raw[s:], s):
            if   ch == s_ch: depth += 1
            elif ch == e_ch: depth -= 1
            if depth == 0:
                return json.loads(raw[s:i + 1])
    return json.loads(raw)


# ══════════════════════════════════════════════════════════════════════════════
# Feature 1 — Resume Scorer
# ══════════════════════════════════════════════════════════════════════════════
def score_resume(resume_text: str, skills: list, level: str) -> dict:
    system = (
        "You are an elite ATS expert and resume coach. "
        "Respond ONLY with valid JSON — no markdown, no preamble. "
        'Schema: {"overall_score":<int 0-100>,'
        '"dimensions":{"impact":{"score":<int 0-10>,"feedback":"<str>"},'
        '"clarity":{"score":<int 0-10>,"feedback":"<str>"},'
        '"ats_compatibility":{"score":<int 0-10>,"feedback":"<str>"},'
        '"skills_presentation":{"score":<int 0-10>,"feedback":"<str>"},'
        '"structure":{"score":<int 0-10>,"feedback":"<str>"}},'
        '"top_strengths":["<str>","<str>","<str>"],'
        '"critical_fixes":["<str>","<str>","<str>"],'
        '"missing_sections":["<str>"],'
        '"ats_keywords_missing":["<str>","<str>","<str>","<str>","<str>"]}'
    )
    user = (
        f"Experience level: {level}\n"
        f"Detected skills: {', '.join(skills[:30])}\n\n"
        f"Resume:\n{resume_text[:3000]}"
    )
    try:
        raw, provider = _call(system, user, 900)
        result = _parse_json(raw)
        result["_provider"] = provider
        return result
    except Exception as e:
        return {"error": str(e), "overall_score": 0}


# ══════════════════════════════════════════════════════════════════════════════
# Feature 2 — Cover Letter Generator
# ══════════════════════════════════════════════════════════════════════════════
def generate_cover_letter(
    resume_text: str, skills: list,
    job_title: str, company: str, job_desc: str,
    tone: str = "professional",
) -> str:
    system = (
        f"You are an expert career writer. Tone: {tone}. "
        "Write a compelling 3-paragraph cover letter: hook → value proposition → CTA. "
        "Reference the actual role and company. No placeholder brackets. "
        "Return ONLY the letter text."
    )
    user = (
        f"Role: {job_title} at {company}\n"
        f"Candidate skills: {', '.join(skills[:25])}\n\n"
        f"Candidate background:\n{resume_text[:1800]}\n\n"
        f"Job description:\n{job_desc[:1500]}"
    )
    try:
        text, _ = _call(system, user, 700)
        return text
    except Exception as e:
        return f"Could not generate cover letter: {e}"


# ══════════════════════════════════════════════════════════════════════════════
# Feature 3 — Interview Coach
# ══════════════════════════════════════════════════════════════════════════════
def generate_interview_prep(
    role: str, skills: list, level: str, job_desc: str = ""
) -> dict:
    system = (
        "You are a senior technical interviewer and career coach. "
        "Respond ONLY with valid JSON — no markdown. "
        'Schema: {"technical_questions":[{"question":"<str>","model_answer":"<str>","difficulty":"easy|medium|hard"}],'
        '"behavioral_questions":[{"question":"<str>","model_answer":"<str>","framework":"STAR"}],'
        '"questions_to_ask_interviewer":["<str>","<str>","<str>"],'
        '"preparation_tips":["<str>","<str>","<str>"],'
        '"red_flags_to_avoid":["<str>","<str>"]}'
        " Include exactly 4 technical and 3 behavioral questions."
    )
    user = (
        f"Role: {role}\nExperience level: {level}\n"
        f"Key skills: {', '.join(skills[:20])}\n"
        f"Job context: {job_desc[:800] if job_desc else 'General role interview'}"
    )
    try:
        raw, provider = _call(system, user, 1400)
        result = _parse_json(raw)
        result["_provider"] = provider
        return result
    except Exception as e:
        return {"error": str(e)}


# ══════════════════════════════════════════════════════════════════════════════
# Feature 4 — Resume Bullet Rewriter
# ══════════════════════════════════════════════════════════════════════════════
def rewrite_resume_bullets(resume_text: str, target_role: str) -> dict:
    system = (
        "You are a tech resume expert. Find the 5 weakest bullet points and rewrite "
        "each with strong action verbs and quantified impact for the target role. "
        "Respond ONLY with valid JSON — no markdown. "
        'Schema: {"rewrites":[{"original":"<exact text>","rewritten":"<improved>","improvement":"<what changed>"}],'
        '"general_advice":"<2 sentences>"}'
    )
    user = f"Target role: {target_role}\n\nResume:\n{resume_text[:3000]}"
    try:
        raw, provider = _call(system, user, 1100)
        result = _parse_json(raw)
        result["_provider"] = provider
        return result
    except Exception as e:
        return {"error": str(e), "rewrites": []}


# ══════════════════════════════════════════════════════════════════════════════
# Feature 5 — Salary Intelligence
# ══════════════════════════════════════════════════════════════════════════════
def extract_salary_intelligence(jobs: list, role: str, country: str) -> dict:
    import re as _re
    pat = _re.compile(
        r"(?:£|€|\$|USD|INR|LPA|lpa)\s*[\d,]+(?:\s*[-–]+\s*(?:£|€|\$)?[\d,]+)?|"
        r"[\d,.]+\s*(?:LPA|lpa|lakhs?|per\s+annum|p\.a\.)",
        _re.I,
    )
    mentions = []
    for job in jobs[:50]:
        mentions.extend(pat.findall(job.get("description", ""))[:2])

    system = (
        "You are a senior compensation analyst with global tech salary benchmarks. "
        "Respond ONLY with valid JSON — no markdown. "
        'Schema: {"estimated_range":{"min":<int>,"max":<int>,"currency":"<ISO code>","period":"annual"},'
        '"median":<int>,'
        '"percentiles":{"p25":<int>,"p50":<int>,"p75":<int>,"p90":<int>},'
        '"factors":["<str>","<str>","<str>"],'
        '"negotiation_tips":["<str>","<str>","<str>"],'
        '"market_context":"<2 sentence summary>"}'
        " Use local currency: INR for India, USD for US/CA/AU/SG, GBP for UK, EUR for Germany."
    )
    user = (
        f"Role: {role}\nCountry: {country}\n"
        f"Live listings analysed: {len(jobs)}\n"
        f"Salary mentions: {mentions[:20] if mentions else 'none found'}"
    )
    try:
        raw, provider = _call(system, user, 700)
        result = _parse_json(raw)
        result["_provider"] = provider
        return result
    except Exception as e:
        return {"error": str(e)}


# ══════════════════════════════════════════════════════════════════════════════
# Feature 6 — Career Path Planner
# ══════════════════════════════════════════════════════════════════════════════
def generate_career_path(
    roles: list, skills: list, level: str, country: str
) -> dict:
    system = (
        "You are a tech career strategist with deep industry knowledge. "
        "Respond ONLY with valid JSON — no markdown. "
        'Schema: {"current_level":"<str>",'
        '"progression":[{"step":<int 1-3>,"title":"<role>","timeline":"<e.g. 0-6 months>",'
        '"skills_to_add":["<str>","<str>","<str>"],"certifications":["<str>"],'
        '"avg_salary_usd":<int>,"description":"<1 sentence>"}],'
        '"skills_roadmap":{"immediate":["<str>","<str>","<str>"],'
        '"short_term":["<str>","<str>","<str>"],'
        '"long_term":["<str>","<str>","<str>"]},'
        '"adjacent_roles":["<str>","<str>","<str>"],'
        '"market_demand":"high|medium|low",'
        '"advice":"<2 sentences>"}'
        " Include exactly 3 progression steps."
    )
    user = (
        f"Current predicted roles: {', '.join(roles[:3])}\n"
        f"Experience level: {level}\n"
        f"Current skills: {', '.join(skills[:25])}\n"
        f"Target market: {country}"
    )
    try:
        raw, provider = _call(system, user, 1000)
        result = _parse_json(raw)
        result["_provider"] = provider
        return result
    except Exception as e:
        return {"error": str(e)}


# ══════════════════════════════════════════════════════════════════════════════
# Feature 7 — Job Fit Analyser
# ══════════════════════════════════════════════════════════════════════════════
def analyse_job_fit(
    resume_text: str, job_title: str, job_desc: str, skills: list
) -> dict:
    system = (
        "You are a precise job-fit analyst. "
        "Respond ONLY with valid JSON — no markdown. "
        'Schema: {"fit_score":<int 0-100>,'
        '"verdict":"Strong Match|Good Fit|Partial Fit|Stretch Role",'
        '"why_you_fit":["<reason>","<str>","<str>"],'
        '"why_you_might_struggle":["<challenge>","<str>"],'
        '"standout_angle":"<1 sentence unique value this candidate brings>",'
        '"application_advice":"<2 sentences>",'
        '"red_flags":["<str>"]}'
    )
    user = (
        f"Job: {job_title}\n"
        f"Candidate skills: {', '.join(skills[:20])}\n\n"
        f"Job description:\n{job_desc[:1500]}\n\n"
        f"Resume:\n{resume_text[:1500]}"
    )
    try:
        raw, provider = _call(system, user, 800)
        result = _parse_json(raw)
        result["_provider"] = provider
        return result
    except Exception as e:
        return {"error": str(e), "fit_score": 0}