from kyc.liveness.interface import LivenessStatus, MockLivenessGate
from kyc.match.interface import MockFaceMatcher


def test_default_biometric_adapters_fail_closed() -> None:
    assert MockFaceMatcher().compare(b"id", b"selfie").similarity == 0.0
    assert MockFaceMatcher().compare(b"", b"selfie").reason == "NO_FACE"
    assert MockLivenessGate().assess(b"clip").status is LivenessStatus.UNAVAILABLE
