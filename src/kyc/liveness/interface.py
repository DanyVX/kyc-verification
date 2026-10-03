from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class LivenessStatus(StrEnum):
    LIVE = "LIVE"
    SPOOF = "SPOOF"
    INSUFFICIENT_QUALITY = "INSUFFICIENT_QUALITY"
    UNAVAILABLE = "UNAVAILABLE"


@dataclass(frozen=True)
class LivenessResult:
    status: LivenessStatus
    score: float | None


class MockLivenessGate:
    def assess(self, clip: bytes) -> LivenessResult:
        return LivenessResult(LivenessStatus.UNAVAILABLE, None)
