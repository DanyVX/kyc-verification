from kyc.ocr.interface import normalize_numeric


def test_numeric_normalization_does_not_need_name_normalization() -> None:
    assert normalize_numeric("O1S B / 2") == "0158.2"
