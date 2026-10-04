from datetime import UTC, datetime, timedelta

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
    assert repository.list_recent()[0].id == session.id


def test_artifact_retention_and_erase(tmp_path) -> None:
    repository = SessionRepository(f"sqlite:///{tmp_path / 'sessions.sqlite3'}")
    session = KycSession()
    repository.save_artifact("session/a/front", session.id, "ciphertext", retention_hours=1)
    assert repository.erase_artifacts(session.id) == ["session/a/front"]
    repository.save_artifact("session/a/front", session.id, "ciphertext", retention_hours=1)
    assert repository.purge_expired_artifacts(datetime.now(UTC) + timedelta(hours=2)) == [
        "session/a/front"
    ]


def test_decision_round_trip(tmp_path) -> None:
    repository = SessionRepository(f"sqlite:///{tmp_path / 'sessions.sqlite3'}")
    session = KycSession()
    repository.save(session)
    repository.save_decision(session.id, '{"verdict":"REVIEW"}')
    assert repository.get_decision(session.id) == '{"verdict":"REVIEW"}'
