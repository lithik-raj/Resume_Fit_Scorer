from pathlib import Path
import fitz


class ResumeParseError(Exception):
    """Raised when a resume cannot be parsed successfully."""
    pass


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from a PDF resume.

    Raises:
        ResumeParseError: If the PDF cannot be opened or contains
        no readable text.
    """

    try:
        document = fitz.open(file_path)
    except Exception as exc:
        raise ResumeParseError(
            "Resume PDF could not be opened. "
            "Please upload a valid PDF file."
        ) from exc

    extracted_pages = []

    try:
        for page in document:
            text = page.get_text("text")

            if text:
                extracted_pages.append(text)

    finally:
        document.close()

    extracted_text = "\n".join(extracted_pages).strip()

    if not extracted_text:
        raise ResumeParseError(
            "Resume could not be read. "
            "Please upload a text-based PDF or TXT resume."
        )

    return extracted_text


def extract_text_from_txt(file_path: str) -> str:
    """
    Extract text from a TXT resume.
    """

    path = Path(file_path)

    try:
        text = path.read_text(encoding="utf-8").strip()
    except UnicodeDecodeError as exc:
        raise ResumeParseError(
            "TXT resume could not be decoded. "
            "Please upload a UTF-8 text file."
        ) from exc
    except OSError as exc:
        raise ResumeParseError(
            "TXT resume could not be read."
        ) from exc

    if not text:
        raise ResumeParseError(
            "Resume file is empty. Please upload a valid resume."
        )

    return text


def extract_resume_text(file_path: str) -> str:
    """
    Detect the file type and extract resume text.
    """

    path = Path(file_path)

    if not path.exists():
        raise ResumeParseError("Resume file was not found.")

    extension = path.suffix.lower()

    if extension == ".pdf":
        return extract_text_from_pdf(str(path))

    if extension == ".txt":
        return extract_text_from_txt(str(path))

    raise ResumeParseError(
        "Unsupported resume format. "
        "Please upload a PDF or TXT file."
    )