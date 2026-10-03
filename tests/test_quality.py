from PIL import Image

from kyc.capture.quality import assess
from kyc.domain import ReasonCode


def test_small_dark_capture_returns_reasons_and_hints() -> None:
    result = assess(Image.new("RGB", (100, 100), "black"))
    assert ReasonCode.INSUFFICIENT_QUALITY in result.reasons
    assert result.hints
