import pdfplumber
from resume_processing.skills import extract_skills_from_text


def extract_text_from_pdf(file_path: str) -> dict:
    """
    Extract text from a multi-page PDF resume
    and extract skills from that text.
    """

    text = ""

    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        if not text.strip():
            raise ValueError("No readable text found in PDF.")

        resume_text = text.strip()

        # NEW STEP — Extract skills
        extracted_skills = extract_skills_from_text(resume_text)

        return {
            "text": resume_text,
            "skills": extracted_skills
        }

    except Exception as e:
        raise RuntimeError(f"Error extracting text from PDF: {e}")