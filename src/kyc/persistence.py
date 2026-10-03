from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import DateTime, String, Text, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    pass


class SessionRow(Base):
    __tablename__ = "kyc_sessions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    state: Mapped[str] = mapped_column(String(32), index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    decision_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    idempotency_keys_json: Mapped[str] = mapped_column(Text, default="[]")


class ArtifactRow(Base):
    __tablename__ = "artifacts"
    key: Mapped[str] = mapped_column(String(160), primary_key=True)
    session_id: Mapped[str] = mapped_column(String(36), index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    ciphertext: Mapped[str] = mapped_column(Text)


def initialize(database_url: str) -> None:
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    engine.dispose()


def expired_artifact_keys(database_url: str, now: datetime | None = None) -> list[str]:
    engine = create_engine(database_url)
    with Session(engine) as db:
        return list(
            db.scalars(
                select(ArtifactRow.key).where(ArtifactRow.expires_at <= (now or datetime.now(UTC)))
            )
        )


def session_key(session_id: UUID) -> str:
    return f"session/{session_id}/"
