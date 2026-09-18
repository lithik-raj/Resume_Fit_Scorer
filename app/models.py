from typing import List
from pydantic import BaseModel, Field


class JobDescriptionRequest(BaseModel):
    job_description: str = Field(
        ...,
        min_length=50,
        description="Job description text to analyze"
    )


class Criterion(BaseModel):
    name: str
    category: str
    weight: float = Field(..., ge=0, le=100)


class CriteriaResponse(BaseModel):
    criteria: List[Criterion]


class CriterionResult(BaseModel):
    criterion: str
    category: str
    weight: float
    evidence: str
    strength: int = Field(..., ge=0, le=5)
    score: float = Field(..., ge=0)
    reasoning: str


class FitAnalysisResponse(BaseModel):
    overall_score: float = Field(..., ge=0, le=100)
    criteria: List[CriterionResult]
    message: str