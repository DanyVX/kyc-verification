from __future__ import annotations

from dataclasses import dataclass

import httpx


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


class HttpFaceMatcher:
    """Adapter for the companion face pipeline's documented authenticated `/v1/verify` endpoint."""

    def __init__(self, base_url: str, api_key: str, timeout_seconds: float = 15.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds

    def compare(self, id_face: bytes, selfie: bytes, request_id: str) -> FaceMatchResult:
        try:
            response = httpx.post(
                f"{self.base_url}/v1/verify",
                files={
                    "image_a": ("id-face.jpg", id_face, "image/jpeg"),
                    "image_b": ("selfie.jpg", selfie, "image/jpeg"),
                },
                headers={"X-API-Key": self.api_key, "X-Request-ID": request_id},
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            return FaceMatchResult(float(response.json()["score"]))
        except (httpx.HTTPError, KeyError, TypeError, ValueError):
            return FaceMatchResult(None, "FACE_SERVICE_UNAVAILABLE")
