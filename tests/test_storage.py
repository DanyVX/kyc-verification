from cryptography.fernet import Fernet

from kyc.storage import EncryptedStore


def test_artifact_is_encrypted_and_erasable() -> None:
    store = EncryptedStore(Fernet.generate_key().decode())
    store.put("session/a", b"synthetic only")
    assert store.get("session/a") == b"synthetic only"
    assert store.erase_prefix("session/") == 1
