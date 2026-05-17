from __future__ import annotations
import re
from resume_processing.skills import extract_skills_from_text


def _clean(text: str) -> str:
    text = re.sub(r'\r\n|\r', '\n', text)
    text = re.sub(r'\x00', '', text)
    text = re.sub(r'[ \t]{2,}', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def detect_experience(text: str):
    patterns_years = [
        r'(\d+)\+?\s+years?\s+of\s+experience',
        r'(\d+)\+?\s+years?\s+experience',
        r'(\d+)\s+yrs?'
    ]

    patterns_months = [
        r'(\d+)\s+months?',
        r'(\d+)\s+mos?'
    ]

    text = text.lower()
    years = 0

    for p in patterns_years:
        m = re.search(p, text)
        if m:
            years = float(m.group(1))
            break

    if years == 0:
        for p in patterns_months:
            m = re.search(p, text)
            if m:
                months = int(m.group(1))
                years = round(months / 12, 2)
                break

    # determine experience level
    if years < 2:
        level = "Entry"
    elif years < 5:
        level = "Mid"
    else:
        level = "Senior"

    return years, level


def extract_text_from_pdf(file_path: str) -> dict:
    text = ""
    pages = 0

    try:
        import pdfplumber
        with pdfplumber.open(str(file_path)) as pdf:
            pages = len(pdf.pages)
            chunks = [p.extract_text(x_tolerance=2, y_tolerance=2) or "" for p in pdf.pages]
            text = "\n".join(chunks)
    except Exception:
        text = ""

    if not text.strip():
        try:
            import PyPDF2
            with open(str(file_path), "rb") as f:
                reader = PyPDF2.PdfReader(f)
                pages = len(reader.pages)
                text = "\n".join(p.extract_text() or "" for p in reader.pages)
        except Exception:
            text = ""

    if not text.strip():
        raise RuntimeError("Could not extract readable text. Ensure the PDF is text-based.")

    cleaned = _clean(text)

    return {
    "text": cleaned,
    "skills": extract_skills_from_text(cleaned),
    "experience": detect_experience(cleaned),
    "pages": pages
}