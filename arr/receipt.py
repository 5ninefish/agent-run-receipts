from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from arr import SCHEMA, __version__
from arr.hashing import receipt_digest, sha256_file, sha256_text
from arr.policy import check_policy, load_policy, paths_from_unified_diff


def _input_record(path: Path | None, *, raw: str | None = None, label: str) -> dict[str, Any]:
    if path is not None:
        digest, nbytes = sha256_file(path)
        return {
            "label": label,
            "path": str(path),
            "sha256": digest,
            "bytes": nbytes,
        }
    text = raw if raw is not None else ""
    encoded = text.encode("utf-8")
    return {
        "label": label,
        "path": None,
        "sha256": sha256_text(text),
        "bytes": len(encoded),
    }


def run_tests(command: str, *, cwd: Path | None, timeout: int) -> dict[str, Any]:
    try:
        proc = subprocess.run(
            command,
            shell=True,
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")
        return {
            "ran": True,
            "timed_out": True,
            "exit_code": None,
            "stdout_sha256": sha256_text(stdout),
            "stderr_sha256": sha256_text(stderr),
        }
    return {
        "ran": True,
        "timed_out": False,
        "exit_code": proc.returncode,
        "stdout_sha256": sha256_text(proc.stdout or ""),
        "stderr_sha256": sha256_text(proc.stderr or ""),
    }


def emit_receipt(
    *,
    diff_path: Path | None,
    transcript_path: Path | None,
    policy_path: Path | None,
    test_command: str | None,
    run_tests_flag: bool,
    cwd: Path | None,
    timeout: int,
    judges: dict[str, Any] | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    diff_text = diff_path.read_text(encoding="utf-8", errors="replace") if diff_path else ""
    transcript_text = (
        transcript_path.read_text(encoding="utf-8", errors="replace") if transcript_path else ""
    )
    policy = load_policy(policy_path)
    changed = paths_from_unified_diff(diff_text)
    policy_result = check_policy(policy, diff_text=diff_text, changed_paths=changed)

    tests: dict[str, Any]
    if run_tests_flag and test_command:
        tests = run_tests(test_command, cwd=cwd, timeout=timeout)
    else:
        tests = {
            "ran": False,
            "timed_out": False,
            "exit_code": None,
            "stdout_sha256": None,
            "stderr_sha256": None,
            "reason": "not requested" if not run_tests_flag else "no test command",
        }

    receipt: dict[str, Any] = {
        "schema": SCHEMA,
        "tool_version": __version__,
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "inputs": {
            "diff": _input_record(diff_path, raw=diff_text, label="diff"),
            "transcript": _input_record(transcript_path, raw=transcript_text, label="transcript"),
            "policy": _input_record(
                policy_path,
                raw=None if policy_path else __import__("json").dumps(policy, sort_keys=True),
                label="policy",
            ),
            "test_command": {
                "label": "test_command",
                "sha256": sha256_text(test_command) if test_command else None,
                "command": test_command,
            },
        },
        "changed_paths": changed,
        "checks": {
            "policy": policy_result,
            "tests": tests,
        },
        "judges": judges or {"note": "optional; omitted in v0 unless supplied"},
    }
    if extra:
        receipt["extra"] = extra
    receipt["receipt_sha256"] = receipt_digest(receipt)
    return receipt
