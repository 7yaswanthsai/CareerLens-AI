from collections import Counter


def infer_market_role(jobs: list) -> str:
    """
    Infer dominant job role from full job titles.
    """

    titles = [
        job.get("title", "").strip().lower()
        for job in jobs
        if job.get("title")
    ]

    if not titles:
        return "Undetermined"

    title_counts = Counter(titles)
    most_common_title, _ = title_counts.most_common(1)[0]

    return most_common_title.title()