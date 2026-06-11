"""Native desktop launcher for AI Readiness Lab.

Double-clicking the installed app runs this: it starts the bundled FastAPI server
on a free localhost port (serving both the API and the built UI), waits until it
is healthy, then opens a native window pointing at it. No browser, no terminal,
no Python install required — PyInstaller bundles the interpreter and all deps.
"""

from __future__ import annotations

import logging
import os
import socket
import sys
import threading
import time
import urllib.request

HOST = "127.0.0.1"
WINDOW_TITLE = "AI Readiness Lab"

log = logging.getLogger("airl.launcher")


def _setup_logging() -> None:
    """Log startup to a file in the config dir. A packaged app has no console
    (console=False), so field issues are otherwise invisible — this is the only
    place an executive (or we) can see what happened."""
    try:
        from app.settings_store import config_dir

        target = config_dir()
        target.mkdir(parents=True, exist_ok=True)
        log_path = target / "launch.log"
        # In a windowed (console=False) PyInstaller build sys.stdout/stderr are
        # None; redirect them so any library that writes to them can't crash or
        # hang the process.
        if sys.stdout is None or sys.stderr is None:
            stream = open(log_path, "a", buffering=1)
            sys.stdout = sys.stdout or stream
            sys.stderr = sys.stderr or stream
        logging.basicConfig(
            level=logging.INFO,
            filename=str(log_path),
            filemode="w",
            format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        )
    except Exception:
        logging.basicConfig(level=logging.INFO)


def ensure_writable_db() -> None:
    """In the packaged app the working dir may be read-only, so point the SQLite
    file at a per-user config dir before anything imports the DB engine."""
    if not getattr(sys, "frozen", False):
        return
    from app.settings_store import config_dir

    target = config_dir()
    target.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("DATABASE_URL", f"sqlite:///{target / 'ai_readiness_lab.db'}")


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((HOST, 0))
        return sock.getsockname()[1]


def run_server(port: int) -> None:
    """Run uvicorn in-process (blocking). Called on a background thread."""
    try:
        import uvicorn

        from app.main import app

        log.info("starting server on port %s", port)
        # Force the pure-Python loop/protocol. uvicorn's "auto" mode imports the
        # native uvloop/httptools, which don't bundle reliably under PyInstaller
        # and can hang the server at startup.
        config = uvicorn.Config(
            app, host=HOST, port=port, log_level="warning", loop="asyncio", http="h11"
        )
        uvicorn.Server(config).run()
    except Exception:
        log.exception("server thread crashed")
        raise


def wait_until_healthy(port: int, timeout: float = 30.0) -> bool:
    """Poll /health until the server answers or the timeout elapses."""
    deadline = time.monotonic() + timeout
    url = f"http://{HOST}:{port}/health"
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1) as response:  # noqa: S310 (localhost)
                if response.status == 200:
                    return True
        except OSError:
            time.sleep(0.2)
    return False


def start_server_thread(port: int) -> threading.Thread:
    thread = threading.Thread(target=run_server, args=(port,), daemon=True)
    thread.start()
    return thread


def _open_in_browser(port: int) -> None:
    """Fallback when no native webview is available: open the default browser and
    keep the server alive so the app still works everywhere."""
    import webbrowser

    url = f"http://{HOST}:{port}"
    webbrowser.open(url)
    print(f"AI Readiness Lab is running at {url} — close this window to quit.")
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        pass


def main() -> None:
    _setup_logging()
    ensure_writable_db()
    port = find_free_port()
    log.info("launching; picked port %s", port)
    start_server_thread(port)
    if not wait_until_healthy(port):
        log.error("server did not become healthy in time")
        raise RuntimeError("AI Readiness Lab server failed to start")
    log.info("server healthy")

    try:
        import webview
    except ImportError:
        _open_in_browser(port)
        return

    webview.create_window(
        WINDOW_TITLE,
        url=f"http://{HOST}:{port}",
        width=1280,
        height=860,
        min_size=(900, 640),
    )
    webview.start()


if __name__ == "__main__":
    main()
