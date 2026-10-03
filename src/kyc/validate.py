from __future__ import annotations

import re
from datetime import date

from kyc.domain import ReasonCode

CNIC_PATTERN = re.compile(r"^\d{5}-\d{7}-\d$")


def normalize_cnic(value: str) -> str:
    digits = re.sub(r"\D", "", value)
    if len(digits) != 13:
        raise ValueError(ReasonCode.INVALID_CNIC_FORMAT.value)
    return f"{digits[:5]}-{digits[5:12]}-{digits[12]}"


def validate_dates(dob: date, issue: date, expiry: date, today: date | None = None, min_age: int = 18) -> list[ReasonCode]:
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
