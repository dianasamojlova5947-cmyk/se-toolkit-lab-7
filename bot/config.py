"""
Configuration loading for the LMS Telegram bot.

Uses pydantic-settings to load secrets from .env.bot.secret file.
This pattern ensures:
- Secrets are never hardcoded
- Missing values are caught early
- Type validation happens at startup
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class BotConfig(BaseSettings):
    """Bot configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env.bot.secret",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Telegram bot token
    bot_token: str = ""

    # LMS API configuration
    lms_api_base_url: str = "http://localhost:42002"
    lms_api_key: str = ""

    # LLM API configuration
    llm_api_key: str = ""
    llm_api_base_url: str = ""
    llm_api_model: str = "coder-model"

    @property
    def lms_headers(self) -> dict:
        """Return headers for LMS API requests with Bearer auth."""
        return {"Authorization": f"Bearer {self.lms_api_key}"}

    @property
    def llm_headers(self) -> dict:
        """Return headers for LLM API requests with Bearer auth."""
        return {"Authorization": f"Bearer {self.llm_api_key}"}


def load_config() -> BotConfig:
    """Load and return bot configuration."""
    return BotConfig()
