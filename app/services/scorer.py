from app.config import load_scoring_config


class ScoringError(Exception):
    """Raised when score calculation fails."""
    pass


def calculate_criterion_score(
    strength: int,
    weight: float,
) -> float:
    """
    Convert a 0–5 evidence strength into a weighted score.

    Example:
        strength = 4
        weight = 20

        score = (4 / 5) * 20
              = 16
    """

    if not isinstance(strength, int):
        raise ScoringError(
            "Strength must be an integer."
        )

    if strength < 0 or strength > 5:
        raise ScoringError(
            "Strength must be between 0 and 5."
        )

    if weight < 0 or weight > 100:
        raise ScoringError(
            "Weight must be between 0 and 100."
        )

    return (strength / 5) * weight


def calculate_overall_score(
    analysis_results: list[dict],
) -> dict:
    """
    Calculate the final resume-fit score.

    Each analysis result must contain:
        criterion
        category
        weight
        evidence
        strength
        reasoning
    """

    if not isinstance(analysis_results, list):
        raise ScoringError(
            "Analysis results must be a list."
        )

    if not analysis_results:
        raise ScoringError(
            "No analysis results were provided."
        )

    # Load weights from configuration.
    config = load_scoring_config()

    scoring_weights = config.get("scoring", {})

    if not scoring_weights:
        raise ScoringError(
            "Scoring configuration is empty."
        )

    # Make sure configuration totals 100.
    configured_total = sum(
        float(weight)
        for weight in scoring_weights.values()
    )

    if abs(configured_total - 100) > 0.01:
        raise ScoringError(
            "Configured scoring weights must total 100."
        )

    processed_results = []
    overall_score = 0.0

    for result in analysis_results:

        required_fields = [
            "criterion",
            "category",
            "evidence",
            "strength",
            "reasoning",
        ]

        for field in required_fields:
            if field not in result:
                raise ScoringError(
                    f"Missing required field: {field}"
                )

        criterion = result["criterion"]
        category = result["category"]
        evidence = result["evidence"]
        strength = result["strength"]
        reasoning = result["reasoning"]

        if category not in scoring_weights:
            raise ScoringError(
                f"Unknown scoring category: {category}"
            )

        # Weight is supplied by the JD extractor,
        # which derives it from scoring.yaml.
        weight = float(
            result.get(
                "weight",
                0
            )
        )

        criterion_score = calculate_criterion_score(
            strength=strength,
            weight=weight,
        )

        overall_score += criterion_score

        processed_results.append(
            {
                "criterion": criterion,
                "category": category,
                "weight": round(weight, 2),
                "evidence": evidence,
                "strength": strength,
                "score": round(criterion_score, 2),
                "reasoning": reasoning,
            }
        )

    # Protect against floating-point rounding.
    overall_score = max(
        0.0,
        min(
            100.0,
            overall_score
        )
    )

    return {
        "overall_score": round(overall_score, 2),
        "criteria": processed_results,
        "message": "Resume fit score calculated successfully.",
    }