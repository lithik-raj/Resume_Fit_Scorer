import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from app.config import load_scoring_config
from app.models import Criterion, CriteriaResponse


load_dotenv()


class JDExtractionError(Exception):
    pass


def get_client():
    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        raise JDExtractionError(
            "OPENROUTER_API_KEY is not configured."
        )

    return OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
    )


def extract_criteria(job_description: str) -> CriteriaResponse:
    if not job_description.strip():
        raise JDExtractionError(
            "Job description cannot be empty."
        )

    try:
        config = load_scoring_config()
        scoring_weights = config.get("scoring", {})

        if not scoring_weights:
            raise JDExtractionError(
                "Scoring configuration is empty."
            )

        if abs(
            sum(float(v) for v in scoring_weights.values()) - 100
        ) > 0.01:
            raise JDExtractionError(
                "Configured scoring weights must total 100."
            )

        client = get_client()

        prompt = f"""
Extract the important job requirements from this job description.

JOB DESCRIPTION:
{job_description}

Allowed categories:
technical_skills
experience
education
projects
soft_skills

Rules:
- Extract only requirements explicitly present.
- Do not invent requirements.
- Avoid duplicates.
- Do not assign weights.
- Return only valid JSON.
- No markdown.

Return:
{{
  "criteria": [
    {{
      "name": "Python",
      "category": "technical_skills"
    }}
  ]
}}
"""

        response = client.chat.completions.create(
            model="openrouter/free",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=0,
            max_tokens=1500,
        )

        output_text = response.choices[0].message.content.strip()

        output_text = output_text.replace(
            "```json", ""
        ).replace(
            "```", ""
        ).strip()

        data = json.loads(output_text)

        criteria_data = data.get("criteria")

        if not isinstance(criteria_data, list) or not criteria_data:
            raise JDExtractionError(
                "No valid criteria were returned."
            )

        extracted = []

        for item in criteria_data:
            name = item.get("name")
            category = item.get("category")

            if not name or category not in scoring_weights:
                continue

            extracted.append(
                {
                    "name": name,
                    "category": category,
                }
            )

        if not extracted:
            raise JDExtractionError(
                "No valid job requirements were extracted."
            )

        category_counts = {}

        for item in extracted:
            category = item["category"]
            category_counts[category] = (
                category_counts.get(category, 0) + 1
            )

        active_total = sum(
            float(scoring_weights[c])
            for c in category_counts
        )

        results = []

        for item in extracted:
            category = item["category"]

            category_weight = (
                float(scoring_weights[category])
                / active_total
                * 100
            )

            criterion_weight = (
                category_weight
                / category_counts[category]
            )

            results.append(
                Criterion(
                    name=item["name"],
                    category=category,
                    weight=criterion_weight,
                )
            )

        return CriteriaResponse(criteria=results)

    except JDExtractionError:
        raise

    except Exception as exc:
        raise JDExtractionError(
            f"OpenRouter request failed: {exc}"
        ) from exc

