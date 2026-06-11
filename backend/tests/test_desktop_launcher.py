"""The desktop launcher's headless helpers (no GUI involved)."""

import importlib.util
from pathlib import Path

# Load desktop/app.py under a unique name so it doesn't collide with the backend
# `app` package. Only the pure helpers are exercised; the webview window is not.
_PATH = Path(__file__).resolve().parents[2] / "desktop" / "app.py"
_spec = importlib.util.spec_from_file_location("desktop_launcher", _PATH)
launcher = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(launcher)


def test_find_free_port_returns_usable_port():
    port = launcher.find_free_port()
    assert isinstance(port, int)
    assert 1024 <= port <= 65535


def test_wait_until_healthy_times_out_on_dead_port():
    # Nothing is listening — must return False promptly, not hang.
    dead_port = launcher.find_free_port()
    assert launcher.wait_until_healthy(dead_port, timeout=0.5) is False
