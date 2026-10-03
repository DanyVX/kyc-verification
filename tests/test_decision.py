from pathlib import Path

from kyc.decision import DecisionEngine
from kyc.domain import ReasonCode, SignalBundle, Verdict


def engine() -> DecisionEngine:
    return DecisionEngine(Path(__file__).parents[1] / "config" / "decision-rules.yaml")


def test_approve_requires_all_passing_signals() -> None:
    result = engine().decide(SignalBundle(ocr_confidence=0.99, face_similarity=0.9, liveness="LIVE"))
    assert result.verdict is Verdict.APPROVE


def test_expired_id_beats_good_face() -> None:
    result = engine().decide(SignalBundle(hard_failures=[ReasonCode.ID_EXPIRED], ocr_confidence=0.99, face_similarity=0.99, liveness="LIVE"))
    assert result.verdict is Verdict.REJECT


def test_liveness_unavailable_never_approves() -> None:
    result = engine().decide(SignalBundle(ocr_confidence=0.99, face_similarity=0.99, liveness=None))
    assert result.verdict is Verdict.REVIEW
