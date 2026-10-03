import pytest

from kyc.ocr.engines import require_engine


def test_known_engine_selection() -> None:
    assert require_engine("paddleocr").language == "en"
    assert require_engine("tesseract").languages == "eng+urd"
    with pytest.raises(ValueError):
        require_engine("unknown")
