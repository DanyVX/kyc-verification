from __future__ import annotations

from collections.abc import Mapping

from kyc.domain import KycSession, ReasonCode, SessionState


class InvalidTransition(ValueError):
    """Raised when an event cannot be applied to the current state."""


TRANSITIONS: Mapping[SessionState, Mapping[str, SessionState]] = {
    SessionState.CREATED: {
        "upload_front": SessionState.ID_FRONT_UPLOADED,
        "cancel": SessionState.CANCELLED,
    },
    SessionState.ID_FRONT_UPLOADED: {
        "upload_back": SessionState.ID_BACK_UPLOADED,
        "cancel": SessionState.CANCELLED,
    },
    SessionState.ID_BACK_UPLOADED: {
        "process_id": SessionState.ID_PROCESSED,
        "cancel": SessionState.CANCELLED,
    },
    SessionState.ID_PROCESSED: {
        "upload_selfie": SessionState.SELFIE_UPLOADED,
        "cancel": SessionState.CANCELLED,
    },
    SessionState.SELFIE_UPLOADED: {
        "complete_liveness": SessionState.LIVENESS_DONE,
        "cancel": SessionState.CANCELLED,
    },
    SessionState.LIVENESS_DONE: {"decide": SessionState.DECIDED, "cancel": SessionState.CANCELLED},
    SessionState.DECIDED: {"review": SessionState.REVIEWED},
    SessionState.REVIEWED: {},
    SessionState.EXPIRED: {},
    SessionState.CANCELLED: {},
}


def apply_event(session: KycSession, event: str, idempotency_key: str) -> KycSession:
    if session.expired() and session.state not in {SessionState.CANCELLED, SessionState.EXPIRED}:
        session.state = SessionState.EXPIRED
        raise InvalidTransition(ReasonCode.SESSION_EXPIRED.value)
    if idempotency_key in session.idempotency_keys:
        return session
    target = TRANSITIONS[session.state].get(event)
    if target is None:
        raise InvalidTransition(f"{ReasonCode.INVALID_TRANSITION.value}: {session.state} + {event}")
    session.state = target
    session.idempotency_keys.add(idempotency_key)
    return session
