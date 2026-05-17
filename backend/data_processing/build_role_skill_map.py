import pandas as pd
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "data"

DATA_DIR.mkdir(exist_ok=True)

relations_path = BASE_DIR / "occupationSkillRelations_en.csv"
skills_path = BASE_DIR / "skills_en.csv"


def build_role_skill_map():

    print("Loading occupation-skill relations...")

    df = pd.read_csv(relations_path)

    role_skill_map = {}

    for _, row in df.iterrows():

        role = str(row["occupationLabel"]).lower().strip()
        skill = str(row["skillLabel"]).lower().strip()

        if role not in role_skill_map:
            role_skill_map[role] = set()

        role_skill_map[role].add(skill)

    # remove weak roles
    filtered_map = {
        role: list(skills)
        for role, skills in role_skill_map.items()
        if len(skills) >= 5
    }

    output_file = DATA_DIR / "role_skill_map.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(filtered_map, f, indent=2)

    print("Role skill map saved:", output_file)
    print("Total roles:", len(filtered_map))


def build_skill_vocabulary():

    print("Loading skills dataset...")

    df = pd.read_csv(skills_path)

    skills = set()

    for _, row in df.iterrows():

        preferred = str(row["preferredLabel"]).lower().strip()

        if preferred:
            skills.add(preferred)

        alt_labels = str(row.get("altLabels", ""))

        if alt_labels and alt_labels != "nan":

            for alt in alt_labels.split("|"):
                alt = alt.strip().lower()
                if alt:
                    skills.add(alt)

    vocab = list(skills)

    output_file = DATA_DIR / "skills_vocabulary.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(vocab, f, indent=2)

    print("Skill vocabulary saved:", output_file)
    print("Total skills:", len(vocab))


if __name__ == "__main__":

    build_role_skill_map()
    build_skill_vocabulary()

    print("Dataset processing completed")