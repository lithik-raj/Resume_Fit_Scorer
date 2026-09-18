# Resume → Job Description Fit Scorer

## 1. Design Parameter — Configuration-Driven Weights

* Scoring weights are stored in `config/scoring.yaml`.
* Weights are not hardcoded inside the scoring logic.
* Current weights:

  * Technical Skills — 50%
  * Experience — 20%
  * Education — 10%
  * Projects — 10%
  * Soft Skills — 10%
* Why:

  * Easy to change weights for different job roles.
  * No code changes are required when adjusting priorities.
  * Keeps the scoring logic transparent and configurable.

## 2. Actual Observed Failure — Invalid LLM Response

* During testing, the LLM sometimes returned:

  * Incomplete JSON
  * Invalid JSON
  * Empty or unexpected response content
* Cause:

  * External LLM responses are not always guaranteed to follow the requested JSON format.
* Fix:

  * Added response validation.
  * Added JSON extraction and parsing checks.
  * Added error handling.
  * Added deterministic text-matching fallback.
* Result:

  * The application can still produce a score when the LLM response cannot be parsed.

## 3. Metric Tracked — Calibration Score Difference

* Metric tracked: **score difference between controlled resume samples**.
* Three sample resumes were tested using the same scoring configuration.
* The calibration script reports:

  * Score for each resume.
  * Difference between Resume A and Resume B.
  * Difference between Resume B and Resume C.
* What it tells:

  * Whether similar resumes receive reasonably similar scores.
  * Whether weaker resumes receive lower scores.
  * Helps identify excessive score variation during calibration.

## 4. Unfinished Work — Larger Calibration Dataset

* Current calibration uses controlled sample resumes.
* A larger real-world dataset has not yet been completed.
* Human evaluation against real recruiter assessments is also pending.
* Next step:

  * Test more real resume and job-description pairs.
  * Compare system scores with human assessments.
  * Tune scoring and calibration based on the results.
