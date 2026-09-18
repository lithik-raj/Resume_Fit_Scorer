const jobDescription = document.getElementById("jobDescription");
const jdCharacterCount = document.getElementById("jdCharacterCount");

const resumeFile = document.getElementById("resumeFile");
const uploadArea = document.getElementById("uploadArea");
const fileName = document.getElementById("fileName");

const analyzeButton = document.getElementById("analyzeButton");
const loadingMessage = document.getElementById("loadingMessage");
const errorMessage = document.getElementById("errorMessage");

const overallScore = document.getElementById("overallScore");
const scoreProgress = document.getElementById("scoreProgress");
const scoreMessage = document.getElementById("scoreMessage");
const resumeFileName = document.getElementById("resumeFileName");
const criteriaContainer = document.getElementById("criteriaContainer");

function updateCharacterCount() {
  if (!jobDescription || !jdCharacterCount) {
    return;
  }

  jdCharacterCount.textContent = jobDescription.value.length;
}

function showError(message) {
  if (!errorMessage) {
    return;
  }

  errorMessage.textContent = message;
  errorMessage.classList.remove("hidden");
}

function hideError() {
  if (!errorMessage) {
    return;
  }

  errorMessage.textContent = "";
  errorMessage.classList.add("hidden");
}

function setLoading(isLoading) {
  if (!analyzeButton || !loadingMessage) {
    return;
  }

  analyzeButton.disabled = isLoading;

  if (isLoading) {
    loadingMessage.classList.remove("hidden");
  } else {
    loadingMessage.classList.add("hidden");
  }
}

function isValidResumeFile(file) {
  if (!file) {
    return false;
  }

  const extension = file.name.split(".").pop().toLowerCase();

  return extension === "pdf" || extension === "txt";
}

function updateSelectedFile(file) {
  if (!file || !fileName) {
    return;
  }

  if (!isValidResumeFile(file)) {
    fileName.textContent = "Choose your resume";

    showError("Unsupported resume format. Please upload a PDF or TXT file.");

    if (resumeFile) {
      resumeFile.value = "";
    }

    return;
  }

  fileName.textContent = file.name;

  hideError();
}

if (jobDescription) {
  jobDescription.addEventListener("input", updateCharacterCount);

  updateCharacterCount();
}

if (resumeFile) {
  resumeFile.addEventListener("change", function () {
    const file = resumeFile.files[0];

    if (file) {
      updateSelectedFile(file);
    }
  });
}

if (uploadArea) {
  uploadArea.addEventListener("dragover", function (event) {
    event.preventDefault();

    uploadArea.classList.add("drag-active");
  });

  uploadArea.addEventListener("dragleave", function () {
    uploadArea.classList.remove("drag-active");
  });

  uploadArea.addEventListener("drop", function (event) {
    event.preventDefault();

    uploadArea.classList.remove("drag-active");

    const file = event.dataTransfer.files[0];

    if (!file) {
      return;
    }

    if (!isValidResumeFile(file)) {
      showError("Unsupported resume format. Please upload a PDF or TXT file.");

      return;
    }

    if (resumeFile) {
      const dataTransfer = new DataTransfer();

      dataTransfer.items.add(file);

      resumeFile.files = dataTransfer.files;
    }

    updateSelectedFile(file);
  });
}

function escapeHtml(value) {
  const div = document.createElement("div");

  div.textContent = String(value ?? "");

  return div.innerHTML;
}

function displayResults(data) {
  if (!overallScore || !scoreProgress || !scoreMessage || !criteriaContainer) {
    return;
  }

  const score = Number(data.overall_score) || 0;

  overallScore.textContent = score.toFixed(2);

  setTimeout(function () {
    scoreProgress.style.width = `${Math.min(Math.max(score, 0), 100)}%`;
  }, 150);

  scoreMessage.textContent = "Analysis completed successfully.";

  if (resumeFileName) {
    resumeFileName.textContent = data.filename || "Resume";
  }

  criteriaContainer.innerHTML = "";

  if (!Array.isArray(data.criteria) || data.criteria.length === 0) {
    criteriaContainer.innerHTML = `<div class="criterion-card">
                <p class="criterion-detail">
                    No criterion results were returned.
                </p>
            </div>`;

    return;
  }

  data.criteria.forEach(function (criterion, index) {
    const strength = Number(criterion.strength) || 0;

    const criterionScore = Number(criterion.score) || 0;

    const strengthPercentage = Math.min(Math.max((strength / 5) * 100, 0), 100);

    const card = document.createElement("article");

    card.className = "criterion-card";

    card.style.animationDelay = `${index * 0.06}s`;

    card.innerHTML = `
                <div class="criterion-top">
                    <div>
                        <div class="criterion-title">
                            ${escapeHtml(criterion.criterion)}
                        </div>

                        <span class="criterion-category">
                            ${escapeHtml(criterion.category)}
                        </span>
                    </div>

                    <div class="criterion-score">
                        <strong>
                            ${criterionScore.toFixed(2)}
                        </strong>

                        <span>
                            ${Number(criterion.weight).toFixed(2)} weight
                        </span>
                    </div>
                </div>

                <div class="strength-bar">
                    <div
                        class="strength-fill"
                        style="width: 0%"
                    ></div>
                </div>

                <div class="criterion-detail">
                    <h4>Evidence</h4>

                    <p>
                        ${escapeHtml(criterion.evidence)}
                    </p>
                </div>

                <div class="criterion-detail">
                    <h4>Strength</h4>

                    <p>
                        ${strength} / 5
                    </p>
                </div>

                <div class="criterion-detail">
                    <h4>Reasoning</h4>

                    <p>
                        ${escapeHtml(criterion.reasoning)}
                    </p>
                </div>
            `;

    criteriaContainer.appendChild(card);

    const strengthFill = card.querySelector(".strength-fill");

    setTimeout(
      function () {
        if (strengthFill) {
          strengthFill.style.width = `${strengthPercentage}%`;
        }
      },
      200 + index * 80,
    );
  });
}

function loadStoredResults() {
  if (!criteriaContainer) {
    return;
  }

  const storedResult = sessionStorage.getItem("resumeFitResult");

  if (!storedResult) {
    if (overallScore) {
      overallScore.textContent = "0";
    }

    if (scoreMessage) {
      scoreMessage.textContent =
        "No analysis result found. Please start a new analysis.";
    }

    return;
  }

  try {
    const data = JSON.parse(storedResult);

    displayResults(data);
  } catch (error) {
    if (scoreMessage) {
      scoreMessage.textContent = "Unable to load the analysis result.";
    }
  }
}

if (analyzeButton) {
  analyzeButton.addEventListener("click", async function () {
    hideError();

    const jdText = jobDescription ? jobDescription.value.trim() : "";

    const selectedFile =
      resumeFile && resumeFile.files.length > 0 ? resumeFile.files[0] : null;

    if (!jdText) {
      showError("Please enter a job description.");

      if (jobDescription) {
        jobDescription.focus();
      }

      return;
    }

    if (jdText.length < 50) {
      showError("Job description must contain at least 50 characters.");

      if (jobDescription) {
        jobDescription.focus();
      }

      return;
    }

    if (!selectedFile) {
      showError("Please upload your resume.");

      return;
    }

    if (!isValidResumeFile(selectedFile)) {
      showError("Unsupported resume format. Please upload a PDF or TXT file.");

      return;
    }

    const formData = new FormData();

    formData.append("job_description", jdText);

    formData.append("resume", selectedFile);

    setLoading(true);

    try {
      const response = await fetch("/analyze", {
        method: "POST",
        body: formData,
      });

      let data;

      try {
        data = await response.json();
      } catch (jsonError) {
        throw new Error("Server returned an invalid response.");
      }

      if (!response.ok) {
        throw new Error(data.detail || "Resume analysis failed.");
      }

      if (data.status !== "success") {
        throw new Error(data.message || "Analysis could not be completed.");
      }

      sessionStorage.setItem("resumeFitResult", JSON.stringify(data));

      window.location.href = "/results";
    } catch (error) {
      showError(
        error.message || "Something went wrong while analyzing the resume.",
      );
    } finally {
      setLoading(false);
    }
  });
}

loadStoredResults();
