"""Secure storage for the user's Anthropic API key.

The packaged desktop app has no environment variables to read, so the key the
executive pastes in Settings is persisted here. Primary storage is the OS
keychain via `keyring` (macOS Keychain, Windows Credential Locker, Linux Secret
Service) — encrypted at rest, never written to the repo or a plaintext config.

When no keychain backend is available (e.g. a headless CI box), we fall back to
a 0600-permissioned JSON file under the user's config dir. The key is never
returned to the UI in full; callers expose only a masked hint.
"""

from __future__ import annotations

import json
import os
import stat
from pathlib import Path

_SERVICE = "ai-readiness-lab"
_USERNAME = "anthropic_api_key"


def config_dir() -> Path:
    """Per-user config dir; overridable with AIRL_CONFIG_DIR (used by tests)."""
    override = os.getenv("AIRL_CONFIG_DIR")
    if override:
        return Path(override)
    if os.name == "nt":
        base = Path(os.getenv("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif os.sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config"))
    return base / "ai-readiness-lab"


def _fallback_file() -> Path:
    return config_dir() / "credentials.json"


def _use_keyring() -> bool:
    """File fallback is forced when AIRL_CONFIG_DIR is set (deterministic tests)."""
    return os.getenv("AIRL_CONFIG_DIR") is None


def _file_read() -> str | None:
    path = _fallback_file()
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text()).get(_USERNAME) or None
    except (ValueError, OSError):
        return None


def _file_write(key: str | None) -> None:
    path = _fallback_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {_USERNAME: key} if key else {}
    path.write_text(json.dumps(data))
    # Restrict to the owner — the key sits in this file.
    path.chmod(stat.S_IRUSR | stat.S_IWUSR)


def get_api_key() -> str | None:
    """Return the stored key, or None. Keychain first, file fallback otherwise."""
    if _use_keyring():
        try:
            import keyring

            value = keyring.get_password(_SERVICE, _USERNAME)
            if value:
                return value
        except Exception:
            pass
    return _file_read()


def set_api_key(key: str) -> None:
    if _use_keyring():
        try:
            import keyring

            keyring.set_password(_SERVICE, _USERNAME, key)
            return
        except Exception:
            pass
    _file_write(key)


def clear_api_key() -> None:
    if _use_keyring():
        try:
            import keyring

            keyring.delete_password(_SERVICE, _USERNAME)
            return
        except Exception:
            pass
    _file_write(None)


def key_hint(key: str | None = None) -> str:
    """A safe display hint — last 4 chars only, never the full secret."""
    key = key if key is not None else get_api_key()
    if not key:
        return ""
    return f"…{key[-4:]}" if len(key) >= 4 else "…"
