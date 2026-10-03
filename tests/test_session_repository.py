from kyc.domain import KycSession, SessionState
from kyc.session_repository import SessionRepository


def test_session_round_trip(tmp_path) -> None:
    repository = SessionRepository(f"sqlite:///{tmp_path / 'sessions.sqlite3'}")
    session = KycSession(state=SessionState.ID_FRONT_UPLOADED, idempotency_keys={"front-1"})
    repository.save(session)
    loaded = repository.get(session.id)
    assert loaded is not None
    assert loaded.state is SessionState.ID_FRONT_UPLOADED
    assert loaded.idempotency_keys == {"front-1"}
