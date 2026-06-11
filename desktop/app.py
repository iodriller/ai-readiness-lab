"""Native desktop launcher for AI Readiness Lab.

Double-clicking the installed app runs this: it starts the bundled FastAPI server
on a free localhost port (serving both the API and the built UI), waits until it
is healthy, then opens a native window pointing at it. No browser, no terminal,
no Python install required — PyInstaller bundles the interpreter and all deps.
"""

from __future__ import annotations

import socket
import threading
import time
import urllib.request

HOST = "127.0.0.1"
WINDOW_TITLE = "AI Readiness Lab"


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((HOST, 0))
        return sock.getsockname()[1]


def run_server(port: int) -> None:
    """Run uvicorn in-process (blocking). Called on a background thread."""
    import uvicorn

    from app.main import app

    uvicorn.run(app, host=HOST, port=port, log_level="warning")


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


def main() -> None:
    import webview

    port = find_free_port()
    start_server_thread(port)
    if not wait_until_healthy(port):
        raise RuntimeError("AI Readiness Lab server failed to start")

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
