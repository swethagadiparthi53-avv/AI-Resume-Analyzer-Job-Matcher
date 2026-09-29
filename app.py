"""AI Resume Analyzer and Job Matcher."""

import json
import os
import re
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

try:
    from openai import OpenAI
except ImportError:  # Keeps the app importable before dependencies are installed.
    OpenAI = None


ROOT = Path(__file__).parent
MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini")
MAX_TEXT = 30_000
MAX_FILE_BYTES = 3 * 1024 * 1024

app = FastAPI(title="AI Resume Analyzer", version="1.0.0")
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")

SKILLS = [
    "python", "java", "javascript", "typescript", "react", "fastapi", "spring boot", "sql",
    "postgresql", "mysql", "mongodb", "rest api", "docker", "git", "github", "aws", "azure",
    "machine learning", "deep learning", "natural language processing", "openai", "pandas",
    "numpy", "scikit-learn", "tensorflow", "communication", "leadership", "problem solving",
    "data structures", "algorithms", "html", "css", "linux", "agile", "testing",
]

ANALYSIS_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "match_score": {"type": "integer", "minimum": 0, "maximum": 100},
        "summary": {"type": "string"},
        "matched_skills": {"type": "array", "items": {"type": "string"}},
        "missing_skills": {"type": "array", "items": {"type": "string"}},
        "strengths": {"type": "array", "items": {"type": "string"}},
        "improvements": {"type": "array", "items": {"type": "string"}},
        "improved_bullets": {"type": "array", "items": {"type": "string"}},
        "interview_questions": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["match_score", "summary", "matched_skills", "missing_skills", "strengths", "improvements", "improved_bullets", "interview_questions"],
}


def load_env_file():
    env_file = ROOT / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def extract_text(filename: str, content: bytes) -> str:
    suffix = Path(filename or "").suffix.lower()
    if suffix in (".txt", ".md", ".text"):
        return content.decode("utf-8", errors="ignore")
    if suffix == ".pdf":
        try:
            from pypdf import PdfReader
            import io

            reader = PdfReader(io.BytesIO(content))
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        except ImportError as error:
            raise ValueError("PDF support needs the pypdf dependency. Run: pip install -r requirements.txt") from error
    raise ValueError("Please upload a .pdf, .txt, or .md resume.")


def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text or "").strip()
    if not text:
        raise ValueError("The uploaded resume appears to be empty.")
    return text[:MAX_TEXT]


def detected_skills(text: str):
    lowered = text.lower()
    return [skill.title() for skill in SKILLS if skill in lowered]


def demo_analysis(resume: str, job_description: str):
    resume_skills = detected_skills(resume)
    job_skills = detected_skills(job_description)
    matched = [skill for skill in job_skills if skill in resume_skills]
    missing = [skill for skill in job_skills if skill not in resume_skills]
    score = round((len(matched) / max(len(job_skills), 1)) * 100)
    return {
        "match_score": score,
        "summary": "Demo analysis complete. Add an OpenAI API key for deeper resume feedback and tailored bullet rewrites.",
        "matched_skills": matched or resume_skills[:5],
        "missing_skills": missing or ["Add the main tools from the job description"],
        "strengths": ["Your resume includes identifiable technical skills.", "The role and resume can be compared automatically.", "You have a clear starting point for tailoring your application."],
        "improvements": ["Add measurable outcomes to project bullets.", "Mirror the job description's important keywords where truthful.", "Mention testing, deployment, or collaboration details when applicable."],
        "improved_bullets": ["Built a user-focused application using relevant technologies and documented the implementation.", "Applied problem-solving and software-development practices to deliver a working project.", "Improved the project experience by validating inputs and handling common user scenarios."],
        "interview_questions": ["Walk me through your most relevant project.", "How would you improve this project for production use?", "Which skill in the job description do you want to strengthen first?"],
    }


def analyze_with_openai(resume: str, job_description: str):
    if not os.getenv("OPENAI_API_KEY") or OpenAI is None:
        result = demo_analysis(resume, job_description)
        result["demo_mode"] = True
        return result

    client = OpenAI()
    instructions = """You are an experienced technical recruiter and resume coach.
Analyze the resume against the job description. Be honest and specific: do not invent experience.
Use only evidence from the resume when describing strengths. A match score should reflect relevant
skills, experience, projects, and evidence, not just keyword count. Suggest truthful improvements.
Return only the requested structured output."""
    prompt = f"""RESUME:\n{resume}\n\nJOB DESCRIPTION:\n{job_description}\n\nAnalyze the fit and produce practical advice for an entry-level candidate."""
    response = client.responses.create(
        model=MODEL,
        instructions=instructions,
        input=prompt,
        max_output_tokens=1400,
        text={"format": {"type": "json_schema", "name": "resume_analysis", "strict": True, "schema": ANALYSIS_SCHEMA}},
    )
    result = json.loads(response.output_text)
    result["demo_mode"] = False
    return result


@app.on_event("startup")
def startup():
    load_env_file()


@app.get("/")
def homepage():
    return FileResponse(ROOT / "static" / "index.html")


@app.get("/api/health")
def health():
    return {"status": "ok", "model": MODEL, "api_configured": bool(os.getenv("OPENAI_API_KEY"))}


@app.post("/api/analyze")
async def analyze(resume: UploadFile = File(...), job_description: str = Form(...)):
    try:
        if not job_description.strip():
            raise ValueError("Please add a job description.")
        content = await resume.read()
        if len(content) > MAX_FILE_BYTES:
            raise ValueError("Please upload a resume smaller than 3 MB.")
        resume_text = clean_text(extract_text(resume.filename or "resume.txt", content))
        job_text = clean_text(job_description)
        return analyze_with_openai(resume_text, job_text)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"Analysis failed: {error}") from error
