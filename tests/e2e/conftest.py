"""Process-level e2e fixtures: real uvicorn + file SQLite + HTTP client."""

from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
from collections.abc import Iterator
from pathlib import Path

import httpx
import pytest


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _wait_until_ready(base_url: str, timeout: float = 15.0) -> None:
    deadline = time.monotonic() + timeout
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            response = httpx.get(f"{base_url}/todos", timeout=0.5)
            if response.status_code == 200:
                return
        except (httpx.HTTPError, OSError) as exc:
            last_error = exc
        time.sleep(0.1)
    raise RuntimeError(f"Server at {base_url} did not become ready") from last_error


def stop_e2e_server(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


def start_e2e_server(
    workdir: Path,
    repo_root: Path,
) -> tuple[subprocess.Popen[str], str]:
    """Start uvicorn with DB file under workdir; return (process, base_url)."""
    port = _free_port()
    base_url = f"http://127.0.0.1:{port}"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo_root)
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "src.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ],
        cwd=str(workdir),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    try:
        _wait_until_ready(base_url)
    except Exception:
        stop_e2e_server(process)
        raise
    return process, base_url


@pytest.fixture()
def e2e_server(tmp_path: Path) -> Iterator[tuple[str, Path]]:
    """Run uvicorn with cwd=tmp_path so ./todos.db stays off the project tree."""
    repo_root = Path(__file__).resolve().parents[2]
    workdir = tmp_path / "app"
    workdir.mkdir()
    process, base_url = start_e2e_server(workdir, repo_root)
    try:
        yield base_url, workdir / "todos.db"
    finally:
        stop_e2e_server(process)


@pytest.fixture()
def e2e_client(e2e_server: tuple[str, Path]) -> Iterator[httpx.Client]:
    base_url, _ = e2e_server
    with httpx.Client(base_url=base_url, timeout=5.0) as client:
        yield client
