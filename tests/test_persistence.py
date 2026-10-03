from kyc.persistence import initialize


def test_schema_initializes_on_sqlite(tmp_path) -> None:
    initialize(f"sqlite:///{tmp_path / 'kyc.sqlite3'}")
