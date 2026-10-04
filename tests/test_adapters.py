from kyc.liveness.interface import LivenessStatus, MockLivenessGate
from kyc.match.interface import HttpFaceMatcher, MockFaceMatcher


def test_default_biometric_adapters_fail_closed() -> None:
    assert MockFaceMatcher().compare(b"id", b"selfie").similarity == 0.0
    assert MockFaceMatcher().compare(b"", b"selfie").reason == "NO_FACE"
    assert MockLivenessGate().assess(b"clip").status is LivenessStatus.UNAVAILABLE


def test_http_face_adapter_fails_closed_on_bad_endpoint() -> None:
    result = HttpFaceMatcher("http://127.0.0.1:1", "test", timeout_seconds=0.01).compare(
        b"id", b"selfie", "test-id"
    )
    assert result.similarity is None
    assert result.reason == "FACE_SERVICE_UNAVAILABLE"
