import httpx

from kyc.liveness.interface import HttpLivenessGate, LivenessStatus


def test_http_liveness_unavailable_on_transport_failure(monkeypatch) -> None:
    def unavailable(*args, **kwargs):
        raise httpx.ConnectError("offline")

    monkeypatch.setattr(httpx, "post", unavailable)
    result = HttpLivenessGate("http://localhost:8001").assess_frames([b"frame"], "test-id")
    assert result.status is LivenessStatus.UNAVAILABLE
