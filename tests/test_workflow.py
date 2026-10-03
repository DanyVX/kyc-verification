from datetime import UTC, datetime, timedelta

import pytest
from hypothesis import given, strategies as st

from kyc.domain import KycSession, SessionState
from kyc.workflow import InvalidTransition, TRANSITIONS, apply_event


def test_double_submit_is_idempotent() -> None:
    session = KycSession()
    first = apply_event(session, "upload_front", "same-key")
    second = apply_event(session, "upload_front", "same-key")
    assert first.state is SessionState.ID_FRONT_UPLOADED
    assert second.state is SessionState.ID_FRONT_UPLOADED


def test_expired_session_cannot_transition() -> None:
    session = KycSession(expires_at=datetime.now(UTC) - timedelta(seconds=1))
    with pytest.raises(InvalidTransition):
        apply_event(session, "upload_front", "key")
    assert session.state is SessionState.EXPIRED


@given(st.lists(st.sampled_from(["upload_front", "upload_back", "process_id", "upload_selfie", "complete_liveness", "decide", "review", "cancel"]), max_size=30))
def test_random_event_sequences_never_create_an_illegal_state(events: list[str]) -> None:
    session = KycSession()
    for index, event in enumerate(events):
        before = session.state
        try:
            apply_event(session, event, str(index))
            assert session.state in TRANSITIONS[before].values()
        except InvalidTransition:
            assert session.state in set(TRANSITIONS) | {SessionState.EXPIRED}
