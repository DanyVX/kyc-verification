from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from typing import Final, Protocol


@dataclass(frozen=True)
class OcrResult:
    fields: dict[str, str]
    confidence: float
    engine: str


class OcrEngine(Protocol):
    def extract(self, image: bytes) -> OcrResult: ...


class OcrUnavailable(RuntimeError):
    """The selected local OCR runtime was not installed or did not respond."""


NUMERIC_REPLACEMENTS: Final[dict[str, str | int | None]] = {"O": "0", "l": "1", "S": "5", "B": "8"}


def normalize_numeric(value: str) -> str:
    """Only numeric fields receive common OCR substitution; names never do."""
    return (
        unicodedata.normalize("NFKC", value)
        .translate(str.maketrans(NUMERIC_REPLACEMENTS))
        .replace(" ", "")
        .replace("/", ".")
    )


class MockOcr:
    """Deterministic development adapter; replace with PaddleOCR/Tesseract adapters."""

    def extract(self, image: bytes) -> OcrResult:
        return OcrResult(fields={}, confidence=0.0, engine="mock")
