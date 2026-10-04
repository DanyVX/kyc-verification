from __future__ import annotations

import re
from datetime import date
from hmac import compare_digest, digest

from kyc.domain import ReasonCode

CNIC_PATTERN = re.compile(r"^\d{5}-\d{7}-\d$")


def normalize_cnic(value: str) -> str:
    digits = re.sub(r"\D", "", value)
    if len(digits) != 13:
        raise ValueError(ReasonCode.INVALID_CNIC_FORMAT.value)
    return f"{digits[:5]}-{digits[5:12]}-{digits[12]}"


def validate_dates(
    dob: date, issue: date, expiry: date, today: date | None = None, min_age: int = 18
) -> list[ReasonCode]:
    today = today or date.today()
    reasons: list[ReasonCode] = []
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    if dob > today or age < min_age or age > 120 or issue < dob or issue > today:
        reasons.append(ReasonCode.IMPLAUSIBLE_DATE)
    if expiry < today:
        reasons.append(ReasonCode.ID_EXPIRED)
    if expiry <= issue:
        reasons.append(ReasonCode.IMPLAUSIBLE_DATE)
    return reasons


def identifier_fingerprint(cnic: str, pepper: str) -> str:
    """Keyed, non-reversible lookup value for duplicate/velocity checks; never log the CNIC."""
    normalized = normalize_cnic(cnic)
    return digest(pepper.encode("utf-8"), normalized.encode("utf-8"), "sha256").hex()


def same_identifier(left: str, right: str, pepper: str) -> bool:
    """Compare normalized front/back identifiers without retaining plaintext values."""
    return compare_digest(
        identifier_fingerprint(left, pepper), identifier_fingerprint(right, pepper)
    )


def compare_front_back(
    front_cnic: str | None, back_cnic: str | None, front_name: str | None, back_name: str | None
) -> list[ReasonCode]:
    """Explain cross-side inconsistency without crashing on absent optional fields."""
    reasons: list[ReasonCode] = []
    if front_cnic is not None and back_cnic is not None:
        try:
            if normalize_cnic(front_cnic) != normalize_cnic(back_cnic):
                reasons.append(ReasonCode.INVALID_CNIC_FORMAT)
        except ValueError:
            reasons.append(ReasonCode.INVALID_CNIC_FORMAT)
    if (
        front_name
        and back_name
        and " ".join(front_name.split()).casefold() != " ".join(back_name.split()).casefold()
    ):
        reasons.append(ReasonCode.INSUFFICIENT_QUALITY)
    return reasons
