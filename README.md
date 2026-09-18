# Resume → Job Description Fit Scorer

An applied-AI system that evaluates how well a resume matches a job description.

## Features

- PDF/TXT resume upload
- AI-based job requirement extraction
- Criterion-by-criterion resume analysis
- Evidence and reasoning
- 0–100 transparent fit score
- Configuration-driven scoring
- Resume parsing error handling
- Calibration testing
- FastAPI web application

## How It Works

```text
Job Description + Resume
          ↓
Requirement Extraction
          ↓
Criterion Analysis
          ↓
Evidence + Strength
          ↓
Weighted Python Scoring
          ↓
Overall Fit Score
```

## Scoring

```text
0 = No evidence
1 = Very weak
2 = Limited
3 = Moderate
4 = Strong
5 = Very strong
```

```text
criterion_score = (strength / 5) × weight
```

Weights are configured in:

```text
config/scoring.yaml
```

## Setup

```powershell
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

Create `.env` with:

```text
OPENAI_API_KEY=your_api_key_here
```

## Testing

```powershell
pytest
```

Calibration:

```powershell
python evaluate_calibration.py
```

## Limitations

- Image-only/scanned PDFs are not supported.
- LLM analysis requires a valid API key.
- Calibration currently uses controlled sample data.

## Technologies

Python, FastAPI, Pydantic, OpenAI API, PyMuPDF, PyYAML, JavaScript, HTML, CSS, Pytest.
