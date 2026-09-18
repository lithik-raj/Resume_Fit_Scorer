from app.config import load_scoring_config
from app.services.scorer import calculate_overall_score


CALIBRATION_SAMPLES = [
    {
        "name": "Resume A",
        "results": [
            {
                "criterion": "Python",
                "category": "technical_skills",
                "weight": 25,
                "evidence": "Strong Python experience.",
                "strength": 5,
                "reasoning": "Strong direct evidence.",
            },
            {
                "criterion": "Machine Learning",
                "category": "technical_skills",
                "weight": 25,
                "evidence": "Multiple machine learning projects.",
                "strength": 4,
                "reasoning": "Strong practical evidence.",
            },
            {
                "criterion": "Experience",
                "category": "experience",
                "weight": 20,
                "evidence": "Relevant internship and project experience.",
                "strength": 3,
                "reasoning": "Moderate relevant experience.",
            },
            {
                "criterion": "Education",
                "category": "education",
                "weight": 10,
                "evidence": "Relevant technical degree.",
                "strength": 5,
                "reasoning": "Strong educational alignment.",
            },
            {
                "criterion": "Projects",
                "category": "projects",
                "weight": 10,
                "evidence": "Several AI and ML projects.",
                "strength": 5,
                "reasoning": "Strong project evidence.",
            },
            {
                "criterion": "Communication",
                "category": "soft_skills",
                "weight": 10,
                "evidence": "Good communication and teamwork.",
                "strength": 4,
                "reasoning": "Good supporting evidence.",
            },
        ],
    },
    {
        "name": "Resume B",
        "results": [
            {
                "criterion": "Python",
                "category": "technical_skills",
                "weight": 25,
                "evidence": "Python experience is present.",
                "strength": 4,
                "reasoning": "Good Python evidence.",
            },
            {
                "criterion": "Machine Learning",
                "category": "technical_skills",
                "weight": 25,
                "evidence": "Basic machine learning projects.",
                "strength": 3,
                "reasoning": "Moderate ML evidence.",
            },
            {
                "criterion": "Experience",
                "category": "experience",
                "weight": 20,
                "evidence": "Limited relevant experience.",
                "strength": 2,
                "reasoning": "Some relevant exposure.",
            },
            {
                "criterion": "Education",
                "category": "education",
                "weight": 10,
                "evidence": "Relevant technical degree.",
                "strength": 4,
                "reasoning": "Good educational alignment.",
            },
            {
                "criterion": "Projects",
                "category": "projects",
                "weight": 10,
                "evidence": "A few technical projects.",
                "strength": 3,
                "reasoning": "Moderate project evidence.",
            },
            {
                "criterion": "Communication",
                "category": "soft_skills",
                "weight": 10,
                "evidence": "Basic communication skills.",
                "strength": 3,
                "reasoning": "Moderate supporting evidence.",
            },
        ],
    },
    {
        "name": "Resume C",
        "results": [
            {
                "criterion": "Python",
                "category": "technical_skills",
                "weight": 25,
                "evidence": "Basic Python exposure.",
                "strength": 3,
                "reasoning": "Some Python evidence.",
            },
            {
                "criterion": "Machine Learning",
                "category": "technical_skills",
                "weight": 25,
                "evidence": "Limited ML exposure.",
                "strength": 2,
                "reasoning": "Limited ML evidence.",
            },
            {
                "criterion": "Experience",
                "category": "experience",
                "weight": 20,
                "evidence": "Very limited relevant experience.",
                "strength": 1,
                "reasoning": "Weak experience evidence.",
            },
            {
                "criterion": "Education",
                "category": "education",
                "weight": 10,
                "evidence": "Relevant undergraduate education.",
                "strength": 4,
                "reasoning": "Good educational alignment.",
            },
            {
                "criterion": "Projects",
                "category": "projects",
                "weight": 10,
                "evidence": "One small technical project.",
                "strength": 2,
                "reasoning": "Limited project evidence.",
            },
            {
                "criterion": "Communication",
                "category": "soft_skills",
                "weight": 10,
                "evidence": "Basic communication ability.",
                "strength": 2,
                "reasoning": "Limited supporting evidence.",
            },
        ],
    },
]


def validate_configuration():
    config = load_scoring_config()

    weights = config.get("scoring", {})

    if not weights:
        raise ValueError(
            "Scoring configuration is empty."
        )

    total = sum(
        float(value)
        for value in weights.values()
    )

    if abs(total - 100) > 0.01:
        raise ValueError(
            "Scoring configuration must total 100."
        )

    return weights


def calculate_sample_score(sample):
    result = calculate_overall_score(
        sample["results"]
    )

    return result["overall_score"]


def main():
    configured_weights = validate_configuration()

    print()
    print("Calibration Evaluation")
    print("======================")
    print()

    print("Configured scoring weights:")

    for category, weight in configured_weights.items():
        print(
            f"{category}: {float(weight):.2f}"
        )

    print()

    scores = {}

    for sample in CALIBRATION_SAMPLES:
        score = calculate_sample_score(sample)

        scores[sample["name"]] = score

        print(
            f"{sample['name']}: "
            f"{score:.2f}/100"
        )

    print()

    similar_difference = abs(
        scores["Resume A"] -
        scores["Resume B"]
    )

    weak_difference = abs(
        scores["Resume B"] -
        scores["Resume C"]
    )

    print(
        "A vs B score difference: "
        f"{similar_difference:.2f} points"
    )

    print(
        "B vs C score difference: "
        f"{weak_difference:.2f} points"
    )

    print()


if __name__ == "__main__":
    main()
