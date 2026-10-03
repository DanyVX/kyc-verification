from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FaceMatchResult:
    similarity: float | None
    reason: str | None = None


class MockFaceMatcher:
    """Stable stand-in until an approved versioned face-match package is configured."""

    def compare(self, id_face: bytes, selfie: bytes) -> FaceMatchResult:
        if not id_face or not selfie:
            return FaceMatchResult(None, "NO_FACE")
        return FaceMatchResult(0.0, "MOCK_NOT_A_BIOMETRIC_RESULT")
