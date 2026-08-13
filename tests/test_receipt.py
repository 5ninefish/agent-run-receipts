import json
import subprocess
import sys
from pathlib import Path

from arr.hashing import receipt_digest
from arr.policy import check_policy, load_policy, paths_from_unified_diff
from arr.receipt import emit_receipt

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "examples"


def test_paths_from_unified_diff():
    diff = (FIXTURES / "ok.diff").read_text()
    assert "src/app.py" in paths_from_unified_diff(diff)


def test_policy_blocks_env_and_secret_literal():
    policy = load_policy(FIXTURES / "policy.json")
    bad = (FIXTURES / "secret.diff").read_text()
    result = check_policy(policy, diff_text=bad, changed_paths=paths_from_unified_diff(bad))
    assert result["pass"] is False
    rules = {v["rule"] for v in result["violations"]}
    assert "deny_path_globs" in rules
    assert "deny_diff_regexes" in rules


def test_emit_hashes_are_stable_for_same_inputs(tmp_path):
    r1 = emit_receipt(
        diff_path=FIXTURES / "ok.diff",
        transcript_path=FIXTURES / "transcript.txt",
        policy_path=FIXTURES / "policy.json",
        test_command="true",
        run_tests_flag=False,
        cwd=None,
        timeout=5,
    )
    r2 = emit_receipt(
        diff_path=FIXTURES / "ok.diff",
        transcript_path=FIXTURES / "transcript.txt",
        policy_path=FIXTURES / "policy.json",
        test_command="true",
        run_tests_flag=False,
        cwd=None,
        timeout=5,
    )
    assert r1["inputs"]["diff"]["sha256"] == r2["inputs"]["diff"]["sha256"]
    assert r1["receipt_sha256"] == receipt_digest(r1)
    # timestamps differ so full-body hashes differ; input hashes must not
    assert r1["created_at"] != "" and r2["created_at"] != ""


def test_cli_fails_on_policy_violation(tmp_path):
    out = tmp_path / "receipt.json"
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "arr",
            "emit",
            "--diff",
            str(FIXTURES / "secret.diff"),
            "--transcript",
            str(FIXTURES / "transcript.txt"),
            "--policy",
            str(FIXTURES / "policy.json"),
            "-o",
            str(out),
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 2
    receipt = json.loads(out.read_text())
    assert receipt["checks"]["policy"]["pass"] is False
    assert receipt["receipt_sha256"]


def test_cli_from_git_uncommitted(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "t@example.com"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=repo, check=True)
    (repo / "a.txt").write_text("one\n", encoding="utf-8")
    subprocess.run(["git", "add", "a.txt"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=repo, check=True, capture_output=True)
    (repo / "a.txt").write_text("two\n", encoding="utf-8")
    out = tmp_path / "receipt.json"
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "arr",
            "emit",
            "--from-git",
            "HEAD",
            "--cwd",
            str(repo),
            "-o",
            str(out),
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    receipt = json.loads(out.read_text())
    assert "a.txt" in receipt["changed_paths"]


def test_cli_passes_clean_diff_without_running_tests(tmp_path):
    out = tmp_path / "receipt.json"
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "arr",
            "emit",
            "--diff",
            str(FIXTURES / "ok.diff"),
            "--transcript",
            str(FIXTURES / "transcript.txt"),
            "--policy",
            str(FIXTURES / "policy.json"),
            "--test-cmd",
            "true",
            "-o",
            str(out),
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0
    receipt = json.loads(out.read_text())
    assert receipt["checks"]["policy"]["pass"] is True
    assert receipt["checks"]["tests"]["ran"] is False
