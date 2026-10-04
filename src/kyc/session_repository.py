from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from kyc.domain import KycSession, SessionState
from kyc.persistence import ArtifactRow, Base, SessionRow


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

    def list_recent(self, limit: int = 100) -> list[KycSession]:
        with Session(self.engine) as db:
            rows = db.scalars(
                select(SessionRow).order_by(SessionRow.created_at.desc()).limit(limit)
            )
            return [
                KycSession(
                    id=UUID(row.id),
                    state=SessionState(row.state),
                    created_at=row.created_at,
                    expires_at=row.expires_at,
                    idempotency_keys=set(json.loads(row.idempotency_keys_json)),
                )
                for row in rows
            ]

    def save_artifact(
        self, key: str, session_id: UUID, ciphertext: str, retention_hours: int
    ) -> None:
        with Session(self.engine) as db:
            row = ArtifactRow(
                key=key,
                session_id=str(session_id),
                ciphertext=ciphertext,
                expires_at=datetime.now(UTC) + timedelta(hours=retention_hours),
            )
            db.merge(row)
            db.commit()

    def erase_artifacts(self, session_id: UUID) -> list[str]:
        with Session(self.engine) as db:
            rows = list(
                db.scalars(select(ArtifactRow).where(ArtifactRow.session_id == str(session_id)))
            )
            keys = [row.key for row in rows]
            for row in rows:
                db.delete(row)
            db.commit()
            return keys

    def purge_expired_artifacts(self, now: datetime | None = None) -> list[str]:
        with Session(self.engine) as db:
            rows = list(
                db.scalars(
                    select(ArtifactRow).where(ArtifactRow.expires_at <= (now or datetime.now(UTC)))
                )
            )
            keys = [row.key for row in rows]
            for row in rows:
                db.delete(row)
            db.commit()
            return keys
