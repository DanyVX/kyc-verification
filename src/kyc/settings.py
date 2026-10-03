from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-only configuration; never log these values."""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="KYC_")
    database_url: str = "sqlite:///./kyc.sqlite3"
    encryption_key: str = "wS4PlcOWVDpQSTOma2xlyXMNNge4N84Yn90tVlk6Jws="  # local demo only
    client_api_key: str = "development-client-key-change-me"
    admin_api_key: str = "development-admin-key-change-me"
    raw_retention_hours: int = 24
    max_upload_bytes: int = 8 * 1024 * 1024


settings = Settings()
