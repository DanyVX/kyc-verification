from __future__ import annotations

from io import BytesIO

from PIL import Image, ImageOps


class DocumentNormalizationError(ValueError):
    pass


def normalize_orientation(payload: bytes) -> bytes:
    """Apply EXIF orientation while preserving a standard PNG artifact for downstream stages."""
    try:
        with Image.open(BytesIO(payload)) as source:
            normalized = ImageOps.exif_transpose(source).convert("RGB")
            output = BytesIO()
            normalized.save(output, format="PNG")
            return output.getvalue()
    except Exception as exc:
        raise DocumentNormalizationError("Image cannot be normalized.") from exc


def perspective_correct(payload: bytes) -> bytes:
    """Optional OpenCV correction boundary; never silently pretends a correction occurred."""
    try:
        import cv2  # type: ignore[import-not-found]  # noqa: F401
    except ImportError as exc:
        raise DocumentNormalizationError(
            "Perspective correction requires the vision optional dependency."
        ) from exc
    # Card contour selection waits for a labeled synthetic evaluation set.
    # Returning an uncorrected image would hide a failed capability, so fail explicitly.
    raise DocumentNormalizationError(
        "Card contour correction is not configured for this template yet."
    )
