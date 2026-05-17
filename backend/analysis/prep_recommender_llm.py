from analysis.llm_engine import generate_text

def generate_preparation_plan(job_title: str, company: str, missing_skills: list):

    prompt = f"""
You are an interview preparation expert.

Provide a structured preparation guide for:

Role: {job_title}

Include:
1. Key technical topics to revise
2. Important practical skills
3. Likely interview question areas
4. Suggested preparation strategy

Keep it structured and concise.
"""

    response = generate_text(prompt, max_tokens=300)

    return response