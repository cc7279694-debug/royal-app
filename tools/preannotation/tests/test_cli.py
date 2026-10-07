"""Breaks caught: unusable CLI, private path leakage and server traversal."""
import importlib
import json
import subprocess
import sys
import threading
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest


ROOT = Path(__file__).resolve().parents[3]


def cli(*args):
    return subprocess.run([sys.executable, "-m", "tools.preannotation", *map(str, args)],
                          cwd=ROOT, capture_output=True, text=True)


def test_cli_exposes_prepare_validate_import_demo_and_local_serve():
    result = cli("--help")
    assert result.returncode == 0, result.stderr
    for name in ["prepare", "presentation", "validate", "import", "demo", "serve"]:
        assert name in result.stdout


def test_cli_refuses_non_private_output_without_creating_directory(tmp_path):
    out = tmp_path / "public-output"
    result = cli("demo", "--out", out)
    assert result.returncode == 2, result.stderr
    assert "outputs/milestone1" in result.stderr
    assert not out.exists()


def test_loopback_server_restricts_hosts_members_and_http_writes(tmp_path):
    try:
        io = importlib.import_module("tools.preannotation.__main__")
    except ImportError:
        pytest.fail("preannotation CLI/server is not implemented")
    # A minimal integrity-valid bundle is created by the real synthetic workflow.
    io.create_demo(tmp_path / "demo")
    server = io.make_server(tmp_path / "demo" / "bundle", 0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        with urlopen(base + "/") as response:
            assert "本地视觉标注审核" in response.read().decode("utf-8")
            assert "connect-src 'none'" in response.headers["Content-Security-Policy"]
        with urlopen(base + "/favicon.ico") as response:
            assert response.status == 204
            assert response.read() == b""
        for route in ["/../human-return.json", "/%2e%2e/source.mp4", "/__sources__/source.mp4"]:
            with pytest.raises(HTTPError) as error:
                urlopen(base + route)
            assert error.value.code == 404
        with pytest.raises(HTTPError) as error:
            urlopen(Request(base + "/review.html", headers={"Host": "attacker.example"}))
        assert error.value.code == 403
        with pytest.raises(HTTPError) as error:
            urlopen(Request(base + "/", method="POST", data=b"attempted write"))
        assert error.value.code == 501
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)
