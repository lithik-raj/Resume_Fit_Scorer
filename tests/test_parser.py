from pathlib import Path

import pytest

from app.services.pdf_parser import (
    ResumeParseError,
    extract_resume_text,
    extract_text_from_txt,
)


def test_extract_text_from_txt(tmp_path):
    resume_file = tmp_path / "resume.txt"

    resume_file.write_text(
        "Python Machine Learning FastAPI",
        encoding="utf-8",
    )

    text = extract_text_from_txt(
        str(resume_file)
    )

    assert "Python" in text
    assert "Machine Learning" in text
    assert "FastAPI" in text


def test_empty_txt_file_raises_error(tmp_path):
    resume_file = tmp_path / "empty.txt"

    resume_file.write_text(
        "",
        encoding="utf-8",
    )

    with pytest.raises(ResumeParseError):
        extract_text_from_txt(
            str(resume_file)
        )


def test_unsupported_file_format(tmp_path):
    resume_file = tmp_path / "resume.docx"

    resume_file.write_text(
        "Sample resume",
        encoding="utf-8",
    )

    with pytest.raises(ResumeParseError):
        extract_resume_text(
            str(resume_file)
        )


def test_missing_file_raises_error(tmp_path):
    resume_file = Path(
        tmp_path / "missing.pdf"
    )

    with pytest.raises(ResumeParseError):
        extract_resume_text(
            str(resume_file)
        )

