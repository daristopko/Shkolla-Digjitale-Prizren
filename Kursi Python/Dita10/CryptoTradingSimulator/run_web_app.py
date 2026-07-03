from __future__ import annotations

import socket
import subprocess
import sys
from pathlib import Path


APP_FILE = Path(__file__).resolve().with_name("streamlit_app.py")


def available_port(start: int = 8501, attempts: int = 20) -> int:
    for port in range(start, start + attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            try:
                probe.bind(("127.0.0.1", port))
            except OSError:
                continue
            return port
    raise RuntimeError(f"No available localhost port found from {start} to {start + attempts - 1}.")


def main() -> int:
    try:
        import streamlit  # noqa: F401
    except ModuleNotFoundError:
        print("Streamlit is not installed.")
        print("Install it with: python -m pip install -r requirements.txt")
        return 1

    port = available_port()
    print(f"Starting Crypto Trading Simulator at http://localhost:{port}")
    command = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(APP_FILE),
        "--server.address",
        "localhost",
        "--server.port",
        str(port),
        "--server.headless",
        "true",
    ]
    return subprocess.call(command)


if __name__ == "__main__":
    raise SystemExit(main())
