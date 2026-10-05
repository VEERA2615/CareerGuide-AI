from io import BytesIO
from pypdf import PdfReader
from . import llm


def pdf_to_text(data: bytes) -> str:
    reader = PdfReader(BytesIO(data))
    return "\n".join((p.extract_text() or "") for p in reader.pages)


def extract_profile(text: str) -> dict:
    system = (
        "You read resumes. Return JSON with keys: skills (list of short strings), "
        "education (list), projects (list), experience (list), certifications (list)."
    )
    return llm.ask_json(system, text[:8000])
