"""Environment-driven settings. Secrets come from the environment, never code."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    log_level: str = "INFO"
    database_url: str = "sqlite:///./ai_readiness_lab.db"

    anthropic_api_key: str | None = None
    tavily_api_key: str | None = None
    serper_api_key: str | None = None

    # Deep-research budget: hard caps so a run is always bounded (spec: streaming
    # research with a time limit). The orchestrator stops collecting once either
    # limit is hit and synthesizes from whatever evidence it has gathered so far.
    research_max_sources: int = 100
    research_timeout_seconds: int = 600


@lru_cache
def get_settings() -> Settings:
    return Settings()
