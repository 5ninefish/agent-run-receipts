from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


DEFAULT_POLICY = {
    "schema": "agent-run-receipt-policy/v0",
    "deny_path_globs": [
        ".env",
        ".env.*",
        "**/.env",
        "**/secrets/**",
        "**/*credential*",
        "**/*id_rsa*",
    ],
    "deny_diff_regexes": [
        r"(?i)(api[_-]?key|secret|password|private[_-]?key)\s*[:=]",
    ],
    "max_diff_bytes": 1_000_000,
}


def load_policy(path: Path | None) -> dict[str, Any]:
    if path is None:
        return dict(DEFAULT_POLICY)
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("policy must be a JSON object")
    merged = dict(DEFAULT_POLICY)
    merged.update(data)
    return merged


def _glob_match(path: str, pattern: str) -> bool:
    from fnmatch import fnmatch

    norm = path[2:] if path.startswith("./") else path
    name = Path(norm).name
    if fnmatch(norm, pattern) or fnmatch(name, pattern):
        return True
    if pattern.startswith("**/") and (
        fnmatch(norm, pattern[3:]) or fnmatch(name, pattern[3:])
    ):
        return True
    return False


def check_policy(policy: dict[str, Any], *, diff_text: str, changed_paths: list[str]) -> dict:
    violations: list[dict[str, str]] = []
    max_bytes = int(policy.get("max_diff_bytes") or 0)
    if max_bytes and len(diff_text.encode("utf-8")) > max_bytes:
        violations.append(
            {
                "rule": "max_diff_bytes",
                "detail": f"diff is {len(diff_text.encode('utf-8'))} bytes; limit {max_bytes}",
            }
        )
    for path in changed_paths:
        for pat in policy.get("deny_path_globs") or []:
            if _glob_match(path, pat):
                violations.append({"rule": "deny_path_globs", "detail": f"{path} matches {pat}"})
    for raw in policy.get("deny_diff_regexes") or []:
        if re.search(raw, diff_text):
            violations.append({"rule": "deny_diff_regexes", "detail": raw})
    return {"pass": not violations, "violations": violations}


def paths_from_unified_diff(diff_text: str) -> list[str]:
    paths: list[str] = []
    for line in diff_text.splitlines():
        if line.startswith("+++ b/") or line.startswith("+++ "):
            token = line.split(None, 1)[1]
            if token.startswith("b/"):
                token = token[2:]
            if token != "/dev/null":
                paths.append(token)
        elif line.startswith("--- a/") or line.startswith("--- "):
            token = line.split(None, 1)[1]
            if token.startswith("a/"):
                token = token[2:]
            if token != "/dev/null":
                paths.append(token)
        elif line.startswith("diff --git "):
            rest = line[len("diff --git ") :]
            for token in rest.split():
                if token.startswith("a/") or token.startswith("b/"):
                    paths.append(token[2:])
    # unique, stable
    seen: set[str] = set()
    out: list[str] = []
    for p in paths:
        if p not in seen and p != "/dev/null":
            seen.add(p)
            out.append(p)
    return out
