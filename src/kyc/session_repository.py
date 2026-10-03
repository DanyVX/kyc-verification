from __future__ import annotations

import json
from uuid import UUID

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from kyc.domain import KycSession, SessionState
from kyc.persistence import Base, SessionRow


class SessionRepository:
    """SQLite/Postgres-compatible durable session store; no PII fields are persisted here."""

    def __init__(self, database_url: str) -> None:
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)

    def save(self, session: KycSession) -> None:
        with Session(self.engine) as db:
            row = db.get(SessionRow, str(session.id))
            if row is None:
                row = SessionRow(
                    id=str(session.id),
                    state=session.state.value,
                    created_at=session.created_at,
                    expires_at=session.expires_at,
                    idempotency_keys_json="[]",
                )
                db.add(row)
            row.state = session.state.value
            row.expires_at = session.expires_at
            row.idempotency_keys_json = json.dumps(sorted(session.idempotency_keys))
            db.commit()

    def get(self, session_id: UUID) -> KycSession | None:
        with Session(self.engine) as db:
            row = db.get(SessionRow, str(session_id))
            if row is None:
                return None
            return KycSession(
                id=UUID(row.id),
                state=SessionState(row.state),
                created_at=row.created_at,
                expires_at=row.expires_at,
                idempotency_keys=set(json.loads(row.idempotency_keys_json)),
            )
