from pathlib import Path
import yaml


BASE_DIR = Path(__file__).resolve().parent.parent
SCORING_CONFIG_PATH = BASE_DIR / "config" / "scoring.yaml"


def load_scoring_config() -> dict:
    """Load scoring weights from the YAML configuration file."""

    if not SCORING_CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"Scoring configuration not found: {SCORING_CONFIG_PATH}"
        )

    with open(SCORING_CONFIG_PATH, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    if not isinstance(config, dict):
        raise ValueError("Invalid scoring configuration format.")

    return config