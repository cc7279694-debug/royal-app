import json
import subprocess
import sys

import pytest

def run(*args):
    return subprocess.run([sys.executable, "-m", "clash_tracker_video", *map(str,args)],
                          capture_output=True, text=True, encoding="utf-8")

def test_cli_inspect(video):
    result = run("inspect", video)
    assert result.returncode == 0
    assert "64" in result.stdout and "48" in result.stdout
    assert "average" in result.stdout.lower()

def test_cli_extract_partial_exit_and_report(video, tmp_path):
    output = tmp_path / "out"
    result = run("extract", video, "--times", 0, 10, "--output", output)
    assert result.returncode == 3
    report = json.loads((output / "report.json").read_text(encoding="utf-8"))
    assert report["status"] == "partial"
    assert report["results"][0]["status"] == "success"
    assert report["results"][1]["status"] == "miss"

@pytest.mark.parametrize("times", [["-1"],["NaN"],["inf"],["0","0"],["1","0"],["oops"]])
def test_cli_bad_times(video, tmp_path, times):
    result = run("extract", video, "--times", *times, "--output", tmp_path / "out")
    assert result.returncode == 2
    assert "error" in result.stderr.lower()
    assert "Traceback" not in result.stderr

def test_cli_local_files_only(tmp_path):
    result = run("inspect", "https://example.com/video.mp4")
    assert result.returncode == 2
    assert "local" in result.stderr.lower()

def test_cli_success(video, tmp_path):
    result = run("extract", video, "--times", 0, 0.1, "--output", tmp_path / "out")
    assert result.returncode == 0

def test_cli_missing_input(tmp_path):
    result = run("inspect", tmp_path / "missing.mp4")
    assert result.returncode == 2
    assert "Traceback" not in result.stderr
