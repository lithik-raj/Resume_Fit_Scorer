import json
import os
import re

import httpx
from dotenv import load_dotenv


load_dotenv()


class ResumeAnalysisError(Exception):
    pass


def fallback_analysis(
    resume_text: str,
    criterion_name: str,
) -> dict:

    resume_lower = resume_text.lower()
    criterion_lower = criterion_name.lower()

    words = [
        word
        for word in re.findall(
            r"[a-zA-Z0-9+#.-]+",
            criterion_lower
        )
        if len(word) > 2
    ]

    matched = [
        word
        for word in words
        if word in resume_lower
    ]

    if not words:
        strength = 0
    else:
        ratio = len(matched) / len(words)

        if ratio >= 0.8:
            strength = 5
        elif ratio >= 0.6:
            strength = 4
        elif ratio >= 0.4:
            strength = 3
        elif ratio >= 0.2:
            strength = 2
        elif ratio > 0:
            strength = 1
        else:
            strength = 0

    if matched:
        evidence = (
            f"Resume contains evidence related to "
            f"{criterion_name}: {', '.join(matched[:5])}."
        )
    else:
        evidence = (
            f"No direct evidence for {criterion_name} "
            f"was found in the resume."
        )

    return {
        "evidence": evidence,
        "strength": strength,
        "reasoning": (
            "Fallback text matching was used because "
            "the LLM response could not be parsed."
        )
    }


def analyze_resume_against_criterion(
    resume_text: str,
    criterion_name: str,
    category: str,
) -> dict:

    if not resume_text or not resume_text.strip():
        raise ResumeAnalysisError(
            "Resume text cannot be empty."
        )

    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        return fallback_analysis(
            resume_text,
            criterion_name
        )

    prompt = f"""
Evaluate this resume against ONE job requirement.

Requirement: {criterion_name}
Category: {category}

Resume:
{resume_text}

Strength:
0 no evidence
1 very weak
2 limited
3 moderate
4 strong
5 very strong

Use only information in the resume.

Return ONLY valid JSON in exactly this format:
{{"evidence":"short evidence","strength":3,"reasoning":"short reason"}}
"""

    payload = {
        "model": "openrouter/free",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0,
        "max_tokens": 800
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = httpx.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )

        if response.status_code != 200:
            return fallback_analysis(
                resume_text,
                criterion_name
            )

        data = response.json()

        choices = data.get("choices", [])

        if not choices:
            return fallback_analysis(
                resume_text,
                criterion_name
            )

        message = choices[0].get("message", {})

        if not isinstance(message, dict):
            return fallback_analysis(
                resume_text,
                criterion_name
            )

        content = message.get("content")

        if not content:
            return fallback_analysis(
                resume_text,
                criterion_name
            )

        if isinstance(content, list):
            parts = []

            for item in content:
                if isinstance(item, dict):
                    text = item.get("text")

                    if text:
                        parts.append(str(text))

            content = "".join(parts)

        content = str(content).strip()

        if not content:
            return fallback_analysis(
                resume_text,
                criterion_name
            )

        content = re.sub(
            r"```(?:json)?",
            "",
            content,
            flags=re.IGNORECASE
        ).strip()

        start = content.find("{")
        end = content.rfind("}")

        if start == -1 or end == -1:
            return fallback_analysis(
                resume_text,
                criterion_name
            )

        json_text = content[start:end + 1]

        try:
            result = json.loads(json_text)

            strength = int(
                result.get("strength", 0)
            )

            strength = max(
                0,
                min(5, strength)
            )

            return {
                "evidence": str(
                    result.get(
                        "evidence",
                        "No evidence found."
                    )
                ).strip(),
                "strength": strength,
                "reasoning": str(
                    result.get(
                        "reasoning",
                        "No reasoning provided."
                    )
                ).strip()
            }

        except Exception:
            return fallback_analysis(
                resume_text,
                criterion_name
            )

    except Exception:
        return fallback_analysis(
            resume_text,
            criterion_name
        )

