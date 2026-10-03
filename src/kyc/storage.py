from __future__ import annotations

from cryptography.fernet import Fernet


class EncryptedStore:
    """Encryption boundary for short-lived synthetic artifacts."""

    def __init__(self, key: str) -> None:
        self._fernet = Fernet(key.encode())
        self._values: dict[str, bytes] = {}

    def put(self, key: str, value: bytes) -> None:
        self._values[key] = self._fernet.encrypt(value)

    def get(self, key: str) -> bytes:
        return self._fernet.decrypt(self._values[key])

    def erase_prefix(self, prefix: str) -> int:
        matches = [key for key in self._values if key.startswith(prefix)]
        for key in matches:
            del self._values[key]
        return len(matches)

    def contains(self, key: str) -> bool:
        return key in self._values
