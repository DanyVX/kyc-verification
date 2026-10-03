from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

import httpx


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


class HttpLivenessGate:
    """Versioned adapter for the companion liveness-detection `/v1/decide` contract."""

    def __init__(self, base_url: str, timeout_seconds: float = 10.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def assess_frames(self, frames: list[bytes], request_id: str) -> LivenessResult:
        files = [
            ("frames", (f"frame-{index}.jpg", frame, "image/jpeg"))
            for index, frame in enumerate(frames)
        ]
        try:
            response = httpx.post(
                f"{self.base_url}/v1/decide",
                files=files,
                headers={"X-Request-ID": request_id},
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            payload = response.json()
        except httpx.HTTPError:
            return LivenessResult(LivenessStatus.UNAVAILABLE, None)
        decision = payload.get("decision")
        if decision == "LIVE":
            return LivenessResult(LivenessStatus.LIVE, payload.get("score"))
        if decision == "SPOOF":
            return LivenessResult(LivenessStatus.SPOOF, payload.get("score"))
        return LivenessResult(LivenessStatus.INSUFFICIENT_QUALITY, payload.get("score"))
