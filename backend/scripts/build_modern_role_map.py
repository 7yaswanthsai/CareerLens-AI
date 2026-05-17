import pandas as pd
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

data_file = BASE_DIR / "data_processing" / "IT_Job_Roles_Skills.csv"

df = pd.read_csv(data_file, encoding="latin1")

role_skill_map = {}
all_skills = set()

for _, row in df.iterrows():

    role = str(row["Job Title"]).lower().strip()

    skills = str(row["Skills"]).lower()

    skills = [s.strip() for s in skills.split(",") if len(s.strip()) > 2]

    role_skill_map[role] = skills

    for s in skills:
        all_skills.add(s)

# save role skill map
with open(BASE_DIR / "data" / "role_skill_map_modern.json", "w") as f:
    json.dump(role_skill_map, f, indent=2)

# save skills vocabulary
with open(BASE_DIR / "data" / "skills_vocabulary_modern.json", "w") as f:
    json.dump(sorted(list(all_skills)), f, indent=2)

print("Roles:", len(role_skill_map))
print("Skills:", len(all_skills))