from __future__ import annotations

from datetime import UTC, datetime

from kyc.persistence import expired_artifact_keys
from kyc.storage import EncryptedStore


def purge_expired(store: EncryptedStore, database_url: str, now: datetime | None = None) -> int:
    """Delete raw artifacts which have passed their configured retention deadline."""
    removed = 0
    for key in expired_artifact_keys(database_url, now or datetime.now(UTC)):
        if store.erase_prefix(key):
            removed += 1
    return removed
