"""Configuration management for the elevator system.

Uses Pydantic settings to load from environment variables.
"""
from datetime import datetime
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Server settings
    port: int = 8000
    host: str = "0.0.0.0"
    reload: bool = False

    # Security settings
    access_code: str = "suffolkproto2025"
    password_expiry: datetime = datetime(2025, 8, 31, 23, 59, 59)

    # Email settings
    resend_api_key: Optional[str] = None
    admin_email: str = "aaronjdrake@adapt-llc.com"
    from_email: str = "onboarding@resend.dev"

    # CORS settings
    cors_origins: list[str] = ["*"]

    # Application settings
    max_floor: int = 20
    min_floor: int = 1

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    def is_password_expired(self) -> bool:
        """Check if the access password has expired."""
        return datetime.utcnow() > self.password_expiry


# Global settings instance
settings = Settings()
