from __future__ import annotations

from io import BytesIO
from pathlib import Path
import tempfile

from PIL import Image

from kyc.ocr.interface import OcrEngine, OcrResult, OcrUnavailable


class TesseractOcr:
    """Best-effort English/Urdu baseline; requires system Tesseract and language packs."""

    def __init__(self, languages: str = "eng+urd") -> None:
        self.languages = languages

    def extract(self, image: bytes) -> OcrResult:
        try:
            import pytesseract  # type: ignore[import-not-found]
        except ImportError as exc:
            raise OcrUnavailable(
                "Install the ocr-tesseract extra and Tesseract language packs."
            ) from exc
        try:
            data = pytesseract.image_to_data(
                Image.open(BytesIO(image)), lang=self.languages, output_type=pytesseract.Output.DICT
            )
        except Exception as exc:
            raise OcrUnavailable("Tesseract did not complete an OCR request.") from exc
        texts = [text.strip() for text in data["text"] if text.strip()]
        confidences = [float(value) for value in data["conf"] if float(value) >= 0]
        confidence = (sum(confidences) / len(confidences) / 100) if confidences else 0.0
        return OcrResult(
            fields={"raw_text": "\n".join(texts)}, confidence=confidence, engine="tesseract"
        )


class PaddleOcr:
    """Primary OCR adapter. Model download/selection is deliberately explicit and opt-in."""

    def __init__(self, language: str = "en") -> None:
        self.language = language

    def extract(self, image: bytes) -> OcrResult:
        try:
            from paddleocr import PaddleOCR  # type: ignore[import-not-found]
        except ImportError as exc:
            raise OcrUnavailable(
                "Install the ocr-paddle extra before selecting PaddleOCR."
            ) from exc
        try:
            engine = PaddleOCR(lang=self.language)
            with tempfile.TemporaryDirectory() as temp_dir:
                image_path = Path(temp_dir) / "input.png"
                image_path.write_bytes(image)
                result = engine.ocr(str(image_path))
        except Exception as exc:
            raise OcrUnavailable("PaddleOCR did not complete an OCR request.") from exc
        lines: list[str] = []
        scores: list[float] = []
        for page in result:
            for _box, (text, score) in page:
                lines.append(text)
                scores.append(float(score))
        return OcrResult(
            fields={"raw_text": "\n".join(lines)},
            confidence=(sum(scores) / len(scores)) if scores else 0.0,
            engine="paddleocr",
        )


def require_engine(name: str) -> OcrEngine:
    if name == "paddleocr":
        return PaddleOcr()
    if name == "tesseract":
        return TesseractOcr()
    raise ValueError(f"Unsupported OCR engine: {name}")
