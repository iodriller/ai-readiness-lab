"""Tests for secure key storage, the settings API, and key resolution."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    # Force the file-fallback backend into a temp dir so tests never touch the
    # real OS keychain and stay deterministic.
    monkeypatch.setenv("AIRL_CONFIG_DIR", str(tmp_path))
    # No environment key by default — each test sets what it needs.
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    # get_settings is cached; clear it so env changes take effect.
    from app.config import get_settings

    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def client():
    return TestClient(app)


def test_store_roundtrip(tmp_path):
    from app import settings_store

    assert settings_store.get_api_key() is None
    settings_store.set_api_key("sk-ant-secret-1234")
    assert settings_store.get_api_key() == "sk-ant-secret-1234"
    assert settings_store.key_hint() == "…1234"
    settings_store.clear_api_key()
    assert settings_store.get_api_key() is None


def test_status_starts_in_sample_mode(client):
    body = client.get("/settings").json()
    assert body["has_api_key"] is False
    assert body["mode"] == "sample"
    assert body["source"] == "none"
    assert body["key_hint"] == ""


def test_put_key_enables_live_mode(client):
    body = client.put("/settings/api-key", json={"api_key": "sk-ant-abcd-5678"}).json()
    assert body["has_api_key"] is True
    assert body["mode"] == "live"
    assert body["source"] == "keychain"
    assert body["key_hint"] == "…5678"


def test_put_rejects_non_anthropic_key(client):
    response = client.put("/settings/api-key", json={"api_key": "totally-wrong"})
    assert response.status_code == 422


def test_delete_key_returns_to_sample_mode(client):
    client.put("/settings/api-key", json={"api_key": "sk-ant-abcd-5678"})
    body = client.delete("/settings/api-key").json()
    assert body["has_api_key"] is False
    assert body["mode"] == "sample"


def test_env_key_reported_as_environment_source(client, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-env-9999")
    from app.config import get_settings

    get_settings.cache_clear()
    body = client.get("/settings").json()
    assert body["mode"] == "live"
    assert body["source"] == "environment"


def test_stored_key_takes_precedence_over_env(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-env-0000")
    from app import settings_store
    from app.config import get_settings
    from app.llm.client import resolve_api_key

    get_settings.cache_clear()
    settings_store.set_api_key("sk-ant-stored-1111")
    assert resolve_api_key() == "sk-ant-stored-1111"


def test_key_never_returned_in_full(client):
    client.put("/settings/api-key", json={"api_key": "sk-ant-supersecretvalue"})
    body = client.get("/settings").json()
    assert "supersecret" not in str(body)
    assert body["key_hint"] == "…alue"
