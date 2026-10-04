from datetime import date

import pytest

from kyc.domain import ReasonCode
from kyc.validate import (
    compare_front_back,
    identifier_fingerprint,
    normalize_cnic,
    same_identifier,
    validate_dates,
)


def test_normalizes_cnic_without_hyphens() -> None:
    assert normalize_cnic("1234512345671") == "12345-1234567-1"


def test_rejects_short_cnic() -> None:
    with pytest.raises(ValueError, match="INVALID_CNIC_FORMAT"):
        normalize_cnic("123")


def test_leap_day_and_expiry() -> None:
    reasons = validate_dates(
        date(2000, 2, 29), date(2020, 1, 1), date(2024, 1, 1), today=date(2025, 1, 1)
    )
    assert ReasonCode.ID_EXPIRED in reasons


def test_identifier_fingerprint_is_normalized_and_keyed() -> None:
    assert same_identifier("12345-1234567-1", "1234512345671", "pepper")
    assert identifier_fingerprint("1234512345671", "pepper") != identifier_fingerprint(
        "1234512345671", "other-pepper"
    )


def test_front_back_inconsistency_has_reason_code() -> None:
    reasons = compare_front_back("12345-1234567-1", "99999-1234567-1", "A  Name", "B Name")
    assert ReasonCode.INVALID_CNIC_FORMAT in reasons
    assert ReasonCode.INSUFFICIENT_QUALITY in reasons
