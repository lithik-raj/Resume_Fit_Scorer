# Resume → Job Description Fit Scorer

An AI-powered application that compares a candidate's resume with a job description and generates a transparent **0–100 resume fit score**.

## Features

* PDF/TXT resume upload
* AI-based job requirement extraction
* Criterion-by-criterion resume analysis
* Evidence, strength, and reasoning
* Transparent 0–100 fit score
* Configuration-driven scoring
* Resume parsing error handling
* LLM response fallback handling
* Calibration testing
* FastAPI web application

## How It Works

```text
Job Description + Resume
          ↓
Job Requirement Extraction
          ↓
Criterion-by-Criterion Analysis
          ↓
Evidence + Strength (0–5)
          ↓
Weighted Python Scoring
          ↓
Overall Fit Score (0–100)
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

Current weights:

```text
Technical Skills = 50%
Experience       = 20%
Education        = 10%
Projects         = 10%
Soft Skills      = 10%
```

## AI / LLM

The project uses **OpenRouter** for:

* Job requirement extraction
* Resume-to-criterion analysis
* Evidence and reasoning generation

Python performs the final weighted score calculation.

If an LLM response cannot be parsed, a deterministic text-matching fallback is used.

## Setup

```powershell
pip install -r requirements.txt
```

Create `.env`:

```text
OPENROUTER_API_KEY=your_api_key_here
```

Start the application:

```powershell
python -m uvicorn app.main:app --http h11
```

Open:

```text
http://127.0.0.1:8000
```

## Testing

Run tests:

```powershell
pytest
```

Run calibration:

```powershell
python evaluate_calibration.py
```

Current calibration:

```text
Resume A = 85/100
Resume B = 63/100
Resume C = 45/100
```

## Limitations

* Image-only/scanned PDFs are not supported.
* LLM analysis requires an OpenRouter API key.
* Calibration currently uses controlled sample data.

## Technologies

Python, FastAPI, Pydantic, OpenRouter, HTTPX, PyMuPDF, PyYAML, JavaScript, HTML, CSS, Pytest.

## Documentation

Project design decisions, observed failure, tracked metric, and unfinished work:

```text
docs/project_explanation.md
```
