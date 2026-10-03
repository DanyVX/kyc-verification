from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from uuid import UUID

from pydantic import BaseModel


class AuditEvent(BaseModel):
    timestamp: datetime
    session_id: UUID
    actor: str
    action: str
    reason_code: str | None = None
    previous_hash: str | None = None
    event_hash: str


class AuditLedger:
    """In-memory append-only chain; persist events in production storage."""
    def __init__(self) -> None:
        self.events: list[AuditEvent] = []

    def append(self, session_id: UUID, actor: str, action: str, reason_code: str | None = None) -> AuditEvent:
        previous = self.events[-1].event_hash if self.events else None
        timestamp = datetime.now(UTC)
        payload = f"{timestamp.isoformat()}|{session_id}|{actor}|{action}|{reason_code}|{previous}"
        event = AuditEvent(timestamp=timestamp, session_id=session_id, actor=actor, action=action, reason_code=reason_code, previous_hash=previous, event_hash=hashlib.sha256(payload.encode()).hexdigest())
        self.events.append(event)
        return event
