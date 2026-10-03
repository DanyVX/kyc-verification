from __future__ import annotations

from datetime import UTC, datetime, timedelta
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class SessionState(StrEnum):
    CREATED = "CREATED"
    ID_FRONT_UPLOADED = "ID_FRONT_UPLOADED"
    ID_BACK_UPLOADED = "ID_BACK_UPLOADED"
    ID_PROCESSED = "ID_PROCESSED"
    SELFIE_UPLOADED = "SELFIE_UPLOADED"
    LIVENESS_DONE = "LIVENESS_DONE"
    DECIDED = "DECIDED"
    REVIEWED = "REVIEWED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


class Verdict(StrEnum):
    APPROVE = "APPROVE"
    REVIEW = "REVIEW"
    REJECT = "REJECT"


class ReasonCode(StrEnum):
    INVALID_TRANSITION = "INVALID_TRANSITION"
    SESSION_EXPIRED = "SESSION_EXPIRED"
    INVALID_CNIC_FORMAT = "INVALID_CNIC_FORMAT"
    ID_EXPIRED = "ID_EXPIRED"
    IMPLAUSIBLE_DATE = "IMPLAUSIBLE_DATE"
    LOW_OCR_CONFIDENCE = "LOW_OCR_CONFIDENCE"
    FACE_MATCH_REVIEW = "FACE_MATCH_REVIEW"
    FACE_MATCH_FAILED = "FACE_MATCH_FAILED"
    LIVENESS_SPOOF = "LIVENESS_SPOOF"
    LIVENESS_UNAVAILABLE = "LIVENESS_UNAVAILABLE"
    INSUFFICIENT_QUALITY = "INSUFFICIENT_QUALITY"
    DUPLICATE_IDENTIFIER = "DUPLICATE_IDENTIFIER"
    IMAGE_TOO_BLURRY = "IMAGE_TOO_BLURRY"
    GLARE_ON_NUMBER = "GLARE_ON_NUMBER"
    GLARE_ON_PHOTO = "GLARE_ON_PHOTO"


class KycSession(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    state: SessionState = SessionState.CREATED
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime = Field(default_factory=lambda: datetime.now(UTC) + timedelta(hours=1))
    idempotency_keys: set[str] = Field(default_factory=set)

    def expired(self, now: datetime | None = None) -> bool:
        return (now or datetime.now(UTC)) >= self.expires_at


class SignalBundle(BaseModel):
    hard_failures: list[ReasonCode] = Field(default_factory=list)
    quality_failures: list[ReasonCode] = Field(default_factory=list)
    ocr_confidence: float | None = None
    face_similarity: float | None = None
    liveness: str | None = None
    duplicate_identifier: bool = False


class Decision(BaseModel):
    verdict: Verdict
    reasons: list[ReasonCode]
    rule_set_version: str
    contributions: dict[str, str]
