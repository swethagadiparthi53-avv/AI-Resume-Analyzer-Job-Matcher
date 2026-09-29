# CareerLens — AI Resume Analyzer and Job Matcher

CareerLens is an internship-ready web application that compares a candidate's resume with a job description. It extracts resume text, identifies relevant skills, calculates a fit score, highlights missing skills, suggests stronger resume bullets, and creates interview questions.

The project is designed for recent graduates and internship applicants who want actionable feedback before applying. It is also a practical portfolio project because it combines a real product workflow with backend APIs, document processing, validation, and an LLM integration.

## What this project demonstrates

- FastAPI backend design
- PDF and text file processing
- OpenAI Responses API integration
- Structured JSON output from an AI model
- Form-data file uploads
- Input validation and file-size limits
- Responsive HTML/CSS/JavaScript frontend
- A useful AI product workflow instead of a generic chatbot

## Features

- Upload `.pdf`, `.txt`, or `.md` resumes
- Paste a job description
- Match score from 0–100
- Matched skills and missing skills
- Strengths and improvement plan
- Improved resume bullet suggestions
- Tailored interview questions
- Demo analysis mode when no API key is configured
- No resume persistence in this demo

## Architecture

```text
Browser
  │  multipart form: resume + job description
  ▼
FastAPI application
  ├── validates file type, size, and text
  ├── extracts text from TXT/Markdown/PDF
  ├── runs demo matching or OpenAI analysis
  └── returns structured JSON
  ▼
CareerLens results dashboard
  ├── match score
  ├── skills and gaps
  ├── rewritten bullets
  └── interview questions
```

The application does not store uploaded resumes. Text is kept in memory during the request and then discarded.

## Project structure

```text
ai-resume-analyzer/
├── app.py                # FastAPI routes, parsing, and AI analysis
├── static/
│   └── index.html        # CareerLens frontend
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variable template
├── .gitignore            # Local secrets and generated files
└── README.md             # Project documentation
```

## Setup

Create a virtual environment and install dependencies:

```bash
cd /Users/mohith/interproj/ai-resume-analyzer
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a local environment file:

```bash
cp .env.example .env
```

Add your OpenAI API key to `.env`:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-5-mini
```

The key is read by the backend only. Never put it in `index.html` or commit `.env`.

## Run

```bash
uvicorn app:app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000).

If no API key is configured, the app still runs in demo mode with deterministic skill matching. Add a valid key for deeper AI analysis, rewriting, and tailored questions.

## Using the application

1. Choose a PDF, TXT, or Markdown resume.
2. Paste the complete job description, including responsibilities and requirements.
3. Select **Analyze my resume**.
4. Review the score, matched skills, focus areas, strengths, and suggested bullets.
5. Use the generated questions to prepare for the interview.

For better results, include project descriptions, technologies, measurable outcomes, and the full job requirements in the input.

## API endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/` | Serves the web application |
| `GET` | `/api/health` | Returns backend and API configuration status |
| `POST` | `/api/analyze` | Accepts a resume file and job description |

Example request with cURL:

```bash
curl -X POST http://127.0.0.1:8000/api/analyze \
  -F "resume=@/path/to/resume.pdf" \
  -F "job_description=We are looking for a Python backend intern with SQL and REST API experience."
```

## Analysis flow

```text
Resume upload + job description
             ↓
       Text extraction
             ↓
    OpenAI structured analysis
             ↓
Match score + skills + improvements + interview questions
```

The backend asks the model to return a strict JSON schema so the frontend can render predictable result cards. The OpenAI Responses API supports structured JSON output through a JSON schema format. See the [official OpenAI API quickstart](https://platform.openai.com/docs/quickstart/make-your-first-api-request) and [Responses API structured-output reference](https://platform.openai.com/docs/api-reference/responses-streaming/response/refusal?lang=python).

## Response fields

The analysis response contains:

| Field | Description |
| --- | --- |
| `match_score` | Estimated fit from 0 to 100 |
| `summary` | Short explanation of the overall fit |
| `matched_skills` | Skills found in both inputs |
| `missing_skills` | Job-relevant skills not found in the resume |
| `strengths` | Evidence-based resume strengths |
| `improvements` | Practical improvements to make before applying |
| `improved_bullets` | Suggested truthful project or experience bullets |
| `interview_questions` | Questions tailored to the role and candidate |
| `demo_mode` | Whether the result used fallback keyword matching |

## Development commands

Check Python syntax:

```bash
python3 -m py_compile app.py
```

Run the local health check:

```bash
curl http://127.0.0.1:8000/api/health
```

Test the analyzer with a file:

```bash
curl -X POST http://127.0.0.1:8000/api/analyze \
  -F "resume=@/path/to/resume.pdf" \
  -F "job_description=Python backend intern with SQL and REST API experience."
```

## Troubleshooting

### `ModuleNotFoundError`

Activate the virtual environment and install dependencies again:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### The UI loads but analysis fails

Check that the API server is running and that `.env` contains a valid `OPENAI_API_KEY`. Without a key, demo mode should still work. If the uploaded PDF is scanned or image-only, use a text-based PDF or add OCR support.

### The API key is exposed

Remove it from source files immediately, rotate the key in the OpenAI dashboard, and keep the replacement in `.env`. The `.gitignore` file is configured to exclude `.env`.

## Important limitations

- Resume text is processed in memory and is not saved by this demo.
- The match score is an AI-assisted estimate, not a hiring decision.
- Scanned/image-only PDFs need OCR support, which is not included yet.
- Demo mode uses keyword matching and should not be treated as a complete analysis.

## Future improvements

- Add PostgreSQL storage for users and analysis history
- Add authentication and private candidate dashboards
- Add DOCX parsing and OCR for scanned resumes
- Add an ATS keyword-density report
- Add export to PDF
- Add automated tests and CI with GitHub Actions
- Add job-description templates and saved comparisons

## Portfolio explanation

> I built CareerLens, a FastAPI-based AI resume analyzer that compares a candidate's resume with a job description. It extracts PDF or text content, sends the inputs to the OpenAI Responses API using a strict JSON schema, and renders the match score, skill gaps, improved resume bullets, and interview questions in a responsive frontend. I also added validation, demo fallback behavior, and secure environment-based API-key handling.

## License

This project is intended for educational and portfolio use.
