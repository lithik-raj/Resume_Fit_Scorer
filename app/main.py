import os
import tempfile
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.models import JobDescriptionRequest
from app.services.jd_extractor import (
    JDExtractionError,
    extract_criteria,
)
from app.services.pdf_parser import (
    ResumeParseError,
    extract_resume_text,
)
from app.services.resume_analyzer import (
    ResumeAnalysisError,
    analyze_resume_against_criterion,
)
from app.services.scorer import (
    ScoringError,
    calculate_overall_score,
)
from app.utils.text_cleaner import clean_text


load_dotenv()


BASE_DIR = Path(__file__).resolve().parent.parent

TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"


app = FastAPI(
    title="Resume Fit Scorer",
    description=(
        "An applied-AI system that evaluates how well a resume "
        "matches a job description."
    ),
    version="1.0.0",
)


app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static",
)


@app.get("/")
def home():
    return FileResponse(
        TEMPLATES_DIR / "index.html"
    )


@app.get("/results")
def results_page():
    return FileResponse(
        TEMPLATES_DIR / "results.html"
    )


@app.get("/health")
def health_check():
    return {
        "message": "Resume Fit Scorer API is running",
        "status": "success",
    }


@app.post("/validate-jd")
def validate_job_description(
    request: JobDescriptionRequest,
):
    return {
        "message": "Job description received successfully.",
        "character_count": len(
            request.job_description
        ),
        "status": "valid",
    }


@app.post("/extract-criteria")
def extract_job_criteria(
    request: JobDescriptionRequest,
):
    try:
        result = extract_criteria(
            request.job_description
        )

        return {
            "status": "success",
            "criteria": [
                {
                    "name": criterion.name,
                    "category": criterion.category,
                    "weight": criterion.weight,
                }
                for criterion in result.criteria
            ],
        }

    except JDExtractionError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {exc}",
        )


@app.post("/analyze")
async def analyze_resume(
    job_description: str = Form(...),
    resume: UploadFile = File(...),
):
    if not job_description.strip():
        raise HTTPException(
            status_code=400,
            detail="Job description cannot be empty.",
        )

    if len(job_description.strip()) < 50:
        raise HTTPException(
            status_code=400,
            detail=(
                "Job description must contain at least "
                "50 characters."
            ),
        )

    if not resume.filename:
        raise HTTPException(
            status_code=400,
            detail="Please upload a resume file.",
        )

    extension = os.path.splitext(
        resume.filename
    )[1].lower()

    if extension not in [".pdf", ".txt"]:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported resume format. "
                "Please upload a PDF or TXT file."
            ),
        )

    temporary_file_path = None

    try:
        file_content = await resume.read()

        if not file_content:
            raise HTTPException(
                status_code=400,
                detail="Uploaded resume file is empty.",
            )

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=extension,
        ) as temporary_file:

            temporary_file.write(
                file_content
            )

            temporary_file_path = (
                temporary_file.name
            )

        try:
            resume_text = extract_resume_text(
                temporary_file_path
            )

        except ResumeParseError as exc:
            raise HTTPException(
                status_code=422,
                detail=str(exc),
            )

        try:
            cleaned_resume = clean_text(
                resume_text
            )

            cleaned_job_description = clean_text(
                job_description
            )

        except (TypeError, ValueError) as exc:
            raise HTTPException(
                status_code=422,
                detail=f"Text processing failed: {exc}",
            )

        try:
            criteria_response = extract_criteria(
                cleaned_job_description
            )

        except JDExtractionError as exc:
            raise HTTPException(
                status_code=502,
                detail=str(exc),
            )

        analysis_results = []

        for criterion in criteria_response.criteria:

            try:
                analysis = (
                    analyze_resume_against_criterion(
                        resume_text=cleaned_resume,
                        criterion_name=criterion.name,
                        category=criterion.category,
                    )
                )

            except ResumeAnalysisError as exc:
                raise HTTPException(
                    status_code=502,
                    detail=(
                        f"Resume analysis failed for "
                        f"'{criterion.name}': {exc}"
                    ),
                )

            analysis_results.append(
                {
                    "criterion": criterion.name,
                    "category": criterion.category,
                    "weight": criterion.weight,
                    "evidence": analysis["evidence"],
                    "strength": analysis["strength"],
                    "reasoning": analysis["reasoning"],
                }
            )

        try:
            final_result = calculate_overall_score(
                analysis_results
            )

        except ScoringError as exc:
            raise HTTPException(
                status_code=500,
                detail=str(exc),
            )

        return {
            "status": "success",
            "filename": resume.filename,
            "overall_score": final_result[
                "overall_score"
            ],
            "criteria": final_result[
                "criteria"
            ],
            "message": final_result[
                "message"
            ],
        }

    finally:
        if temporary_file_path:

            try:
                os.remove(
                    temporary_file_path
                )

            except OSError:
                pass
