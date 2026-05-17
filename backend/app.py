import asyncio
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

from job_fetching.adzuna_client import fetch_jobs_async
from matching.matcher import rank_jobs_by_similarity
from resume_processing.parser import extract_text_from_pdf
from resume_processing.skills import extract_skills_from_text
from role_inference.role_predictor import predict_roles
from utils.helpers import clean_text
from analysis.skill_gap import analyze_skill_gap
from market_intelligence.intelligence_engine import generate_career_summary


async def fetch_all_roles(top_roles, country):
    tasks = []

    for role in top_roles:
        tasks.append(
            fetch_jobs_async(role, country=country, results_per_page=10)
        )
        await asyncio.sleep(1)

    results = await asyncio.gather(*tasks)

    all_jobs = []

    for job_list in results:
        all_jobs.extend(job_list)

    # Job Deduplication
    unique_jobs = {}

    for job in all_jobs:
        unique_jobs[job["id"]] = job

    all_jobs = list(unique_jobs.values())

    return all_jobs


def main(resume_path):

    print("\n🔍 Processing Resume...\n")

    parsed_resume = extract_text_from_pdf(resume_path)

    raw_text = parsed_resume["text"]

    cleaned_text = clean_text(raw_text)

    # ===============================
    # SKILL EXTRACTION
    # ===============================
    resume_skills = extract_skills_from_text(cleaned_text)

    print("\n🧠 Extracted Skills:")
    print(resume_skills)

    # ===============================
    # ROLE PREDICTION
    # ===============================
    print("\n🔎 Predicting career roles...")

    top_roles = predict_roles(cleaned_text, resume_skills)

    print("\n🎯 Predicted Roles:")
    for r in top_roles:
        print("-", r)

    country = input("\nEnter country code (us, in, gb, etc): ").lower()

    # ===============================
    # JOB FETCHING
    # ===============================
    print("\n⚡ Fetching role-specific jobs in parallel...")

    all_jobs = asyncio.run(fetch_all_roles(top_roles, country))

    # ===============================
    # CAREER INTELLIGENCE
    # ===============================
    print("\n🚀 Generating Career Intelligence Summary...\n")

    summary = asyncio.run(
        generate_career_summary(cleaned_text, resume_skills, top_roles, all_jobs)
    )

    print("🎯 Top Career Directions:")
    for role in summary["top_roles"]:
        print("-", role)

    print("\n🧭 Emerging Roles From Market:")
    for role in summary["discovered_roles"]:
        print("-", role)

    print("\n📊 Market Strength Score:", summary["market_strength_score"])

    print("\n🔥 Top Market Skills:")
    for skill, freq in summary["top_market_skills"]:
        print(f"- {skill} ({freq})")

    print("\n⚠ Missing High Impact Skills:")
    for item in summary["missing_high_impact_skills"]:
        print(f"- {item['skill']} (Market Demand: {item['market_frequency']})")

    print("\n📈 Skill ROI Simulation:")
    for item in summary["roi_simulation"]:
        print(f"- Adding '{item['skill']}' → +{item['improvement_percent']}% ranking uplift")

    # ===============================
    # JOB MATCHING
    # ===============================
    ranked_jobs = rank_jobs_by_similarity(cleaned_text, all_jobs)

    print("\n🏆 Top 20 Matching Jobs:\n")

    for job in ranked_jobs[:20]:

        print(f"Title: {job['title']}")
        print(f"Company: {job.get('company', {}).get('display_name', 'N/A')}")
        print(f"Location: {job.get('location', {}).get('display_name', 'N/A')}")
        print(f"Match Score: {job['match_score']}%")
        print(f"Apply Link: {job['redirect_url']}")

        gap_analysis = analyze_skill_gap(cleaned_text, job["description"])

        print("\nStrongly Aligned Competencies:")
        for item in gap_analysis["strong_match"]:
            print("-", item)

        print("\nPartially Aligned:")
        for item in gap_analysis["partial_match"]:
            print("-", item)

        print("\nMissing / Weak Areas:")
        for item in gap_analysis["missing"]:
            print("-", item)

        print("-" * 50)


if __name__ == "__main__":
    resume_file_path = "resume.pdf"
    main(resume_file_path)