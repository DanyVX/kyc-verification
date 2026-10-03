from __future__ import annotations

from dataclasses import dataclass

from PIL import Image, ImageFilter, ImageStat

from kyc.domain import ReasonCode


@dataclass(frozen=True)
class QualityResult:
    reasons: list[ReasonCode]
    hints: list[str]


def assess(image: Image.Image) -> QualityResult:
    """Lightweight CPU quality gate. Targeted glare locations require document ROIs."""
    gray = image.convert("L")
    stat = ImageStat.Stat(gray)
    reasons: list[ReasonCode] = []
    hints: list[str] = []
    if image.width < 400 or image.height < 250:
        reasons.append(ReasonCode.INSUFFICIENT_QUALITY)
        hints.append("Move closer so the entire card is readable.")
    if stat.mean[0] < 35:
        reasons.append(ReasonCode.INSUFFICIENT_QUALITY)
        hints.append("Increase even lighting; avoid a dark capture.")
    highlights = sum(pixel >= 245 for pixel in gray.getdata()) / (image.width * image.height)
    if highlights > 0.15:
        reasons.append(ReasonCode.GLARE_ON_NUMBER)
        hints.append("Tilt the card to remove glare from the number area.")
    # Difference from a blurred copy is a conservative blur proxy without OpenCV.
    blurred = gray.filter(ImageFilter.GaussianBlur(radius=2))
    detail = sum(abs(a - b) for a, b in zip(gray.getdata(), blurred.getdata(), strict=True)) / (image.width * image.height)
    if detail < 2:
        reasons.append(ReasonCode.IMAGE_TOO_BLURRY)
        hints.append("Hold the camera steady and refocus before capturing again.")
    return QualityResult(reasons, hints)
