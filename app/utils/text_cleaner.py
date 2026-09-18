import re


def clean_text(text: str) -> str:
    if not isinstance(text, str):
        raise TypeError("Text must be a string.")

    text = text.replace("\r\n", "\n").replace("\r", "\n")

    text = re.sub(r"[ \t]+", " ", text)

    text = re.sub(r"\n{3,}", "\n\n", text)

    lines = [
        line.strip()
        for line in text.split("\n")
    ]

    lines = [
        line
        for line in lines
        if line
    ]

    cleaned = "\n".join(lines).strip()

    if not cleaned:
        raise ValueError(
            "Text is empty after cleaning."
        )

    return cleaned

