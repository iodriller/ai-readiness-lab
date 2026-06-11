"""The bundled-SPA directory resolver (app.main._static_dir)."""

from app.main import _static_dir


def test_static_dir_uses_override_when_valid(tmp_path, monkeypatch):
    (tmp_path / "index.html").write_text("<!doctype html><title>AIRL</title>")
    monkeypatch.setenv("AIRL_STATIC_DIR", str(tmp_path))
    assert _static_dir() == tmp_path


def test_static_dir_ignores_override_without_index(tmp_path, monkeypatch):
    # A dir with no index.html is not a valid build — must not be selected.
    monkeypatch.setenv("AIRL_STATIC_DIR", str(tmp_path))
    result = _static_dir()
    assert result != tmp_path
