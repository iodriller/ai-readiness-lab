"""Settings API — lets the executive enable live research by pasting their key.

The key is stored in the OS keychain (see app.settings_store). The full secret is
never returned to the UI; only a masked hint and a live/sample mode flag.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.config import get_settings
from app.settings_store import clear_api_key, get_api_key, key_hint, set_api_key

router = APIRouter(prefix="/settings", tags=["settings"])


class SettingsStatus(BaseModel):
    has_api_key: bool
    key_hint: str
    mode: str  # "live" when research uses Claude; "sample" otherwise
    source: str  # "keychain" | "environment" | "none"


class ApiKeyRequest(BaseModel):
    api_key: str = Field(min_length=1)


def _status() -> SettingsStatus:
    stored = get_api_key()
    env_key = get_settings().anthropic_api_key
    resolved = stored or env_key
    if stored:
        source = "keychain"
    elif env_key:
        source = "environment"
    else:
        source = "none"
    return SettingsStatus(
        has_api_key=bool(resolved),
        key_hint=key_hint(resolved),
        mode="live" if resolved else "sample",
        source=source,
    )


@router.get("", response_model=SettingsStatus)
def get_settings_status() -> SettingsStatus:
    return _status()


@router.put("/api-key", response_model=SettingsStatus)
def put_api_key(request: ApiKeyRequest) -> SettingsStatus:
    key = request.api_key.strip()
    # Anthropic keys are prefixed `sk-ant-`; reject obvious mistakes early so the
    # exec gets immediate feedback instead of a silent fallback to sample mode.
    if not key.startswith("sk-ant-"):
        raise HTTPException(
            status_code=422,
            detail="That doesn't look like an Anthropic API key (it should start with 'sk-ant-').",
        )
    set_api_key(key)
    return _status()


@router.delete("/api-key", response_model=SettingsStatus)
def delete_api_key() -> SettingsStatus:
    clear_api_key()
    return _status()
