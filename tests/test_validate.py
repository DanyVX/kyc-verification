from datetime import date

import pytest

from kyc.domain import ReasonCode
from kyc.validate import normalize_cnic, validate_dates


def test_normalizes_cnic_without_hyphens() -> None:
    assert normalize_cnic("1234512345671") == "12345-1234567-1"


def test_rejects_short_cnic() -> None:
    with pytest.raises(ValueError, match="INVALID_CNIC_FORMAT"):
        normalize_cnic("123")


def test_leap_day_and_expiry() -> None:
    reasons = validate_dates(date(2000, 2, 29), date(2020, 1, 1), date(2024, 1, 1), today=date(2025, 1, 1))
    assert ReasonCode.ID_EXPIRED in reasons
