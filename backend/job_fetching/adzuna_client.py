"""
job_fetching/adzuna_client.py  —  Production Adzuna client
• build_search_queries() generates diverse targeted queries
• Exponential backoff on rate limits
• Deduplication by title+company
"""
from __future__ import annotations
import asyncio, httpx, os, re
from itertools import cycle
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env")
APP_ID    = os.getenv("ADZUNA_APP_ID","")
KEY_LIST  = [k.strip() for k in os.getenv("ADZUNA_APP_KEYS","").split(",") if k.strip()] or ["__missing__"]
_keys     = cycle(KEY_LIST)

_CLUSTER_Q = [
    ({"machine learning","scikit-learn","pandas","python"},        ["data scientist","machine learning engineer"],   3),
    ({"pytorch","tensorflow","deep learning","neural networks"},   ["machine learning engineer","ai engineer"],       2),
    ({"natural language processing","transformers","bert","spacy"},["nlp engineer","nlp scientist"],                  2),
    ({"computer vision","opencv","image classification"},          ["computer vision engineer"],                      2),
    ({"large language models","langchain","rag pipeline"},         ["llm engineer","generative ai engineer"],         2),
    ({"mlflow","airflow","mlops","sagemaker"},                     ["mlops engineer","ml platform engineer"],         2),
    ({"power bi","tableau","sql","excel"},                         ["data analyst","business analyst"],               3),
    ({"pyspark","kafka","dbt","data pipeline","etl"},              ["data engineer","big data engineer"],             2),
    ({"react","javascript","typescript","html"},                   ["frontend developer","react developer"],          3),
    ({"fastapi","flask","django","rest api"},                      ["backend developer","software engineer"],         2),
    ({"docker","kubernetes","terraform","ci/cd"},                  ["devops engineer","site reliability engineer"],   3),
    ({"aws","azure","gcp","cloud"},                                ["cloud engineer","cloud architect"],              2),
    ({"figma","user research","wireframing"},                      ["ux designer","product designer"],                2),
    ({"penetration testing","security audits"},                    ["security engineer","cybersecurity analyst"],     2),
    ({"kotlin","android sdk"},                                     ["android developer","mobile developer"],          2),
    ({"swift","ios","xcode"},                                      ["ios developer","mobile developer"],              2),
]

_PREFIX = {"Fresher":"","Junior":"junior ","Mid-Level":"","Senior":"senior "}

def build_search_queries(roles, skills, level="Mid-Level", max_queries=7):
    ss   = {s.lower() for s in skills}
    pfx  = _PREFIX.get(level,"")
    seen = set()
    out  = []
    def add(q):
        k = re.sub(r"\s+"," ",q.lower().strip())
        if k not in seen: seen.add(k); out.append(q)
    for r in roles[:4]: add(f"{pfx}{r.strip().lower()}".strip())
    for cluster, titles, min_n in _CLUSTER_Q:
        if len(frozenset(cluster) & ss) >= min_n:
            for t in titles: add(f"{pfx}{t}".strip())
        if len(out) >= max_queries+3: break
    return out[:max_queries]

async def fetch_jobs_async(query, country="us", pages=4, results_per_page=20):
    results, retries = [], 3
    async with httpx.AsyncClient(timeout=30) as client:
        for page in range(1, pages+1):
            url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/{page}"
            for attempt in range(retries):
                try:
                    resp = await client.get(url, params={
                        "app_id": APP_ID, "app_key": next(_keys),
                        "what": query, "results_per_page": results_per_page})
                    if resp.status_code == 429:
                        await asyncio.sleep(2**attempt); continue
                    resp.raise_for_status()
                    results.extend(resp.json().get("results",[]))
                    break
                except httpx.ReadTimeout: await asyncio.sleep(2**attempt)
                except httpx.HTTPStatusError as e:
                    if e.response.status_code >= 500: await asyncio.sleep(2)
                    break
                except httpx.HTTPError: break
    unique = {}
    for j in results:
        k = j.get("title","").lower().strip() + "|" + str(j.get("company",{}).get("display_name","")).lower().strip()
        unique[k] = j
    return list(unique.values())