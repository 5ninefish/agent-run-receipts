from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from arr.receipt import emit_receipt


def _path(value: str | None) -> Path | None:
    return Path(value) if value else None


def write_git_diff(base: str, dest: Path, cwd: Path | None) -> None:
    r = subprocess.run(
        ["git", "diff", "--no-ext-diff", base],
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        check=False,
    )
    if r.returncode != 0:
        raise SystemExit(f"git diff failed: {r.stderr.strip() or r.stdout.strip()}")
    dest.write_text(r.stdout, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="arr",
        description="Emit a verifiable receipt for one agent-produced change.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    emit = sub.add_parser("emit", help="hash inputs, check policy, optionally run tests")
    src = emit.add_mutually_exclusive_group(required=True)
    src.add_argument("--diff", help="unified diff file")
    src.add_argument(
        "--from-git",
        metavar="BASE",
        nargs="?",
        const="HEAD",
        help="use `git diff BASE` (default BASE=HEAD = uncommitted changes)",
    )
    emit.add_argument("--transcript", help="agent transcript / tool log")
    emit.add_argument("--policy", help="JSON policy file (default built-in deny list)")
    emit.add_argument("--test-cmd", help="command whose exit code is recorded")
    emit.add_argument("--run-tests", action="store_true", help="actually execute --test-cmd")
    emit.add_argument("--cwd", help="working directory for git / --test-cmd")
    emit.add_argument("--timeout", type=int, default=120)
    emit.add_argument("-o", "--output", help="write receipt JSON here (default stdout)")

    args = p.parse_args(argv)
    if args.cmd == "emit":
        tmp = None
        diff_path = _path(args.diff)
        if args.from_git is not None:
            tmp = tempfile.NamedTemporaryFile("w", suffix=".diff", delete=False)
            tmp.close()
            diff_path = Path(tmp.name)
            write_git_diff(args.from_git, diff_path, _path(args.cwd))
        receipt = emit_receipt(
            diff_path=diff_path,
            transcript_path=_path(args.transcript),
            policy_path=_path(args.policy),
            test_command=args.test_cmd,
            run_tests_flag=args.run_tests,
            cwd=_path(args.cwd),
            timeout=args.timeout,
        )
        text = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
        if args.output:
            Path(args.output).write_text(text, encoding="utf-8")
        else:
            sys.stdout.write(text)
        if tmp is not None:
            Path(tmp.name).unlink(missing_ok=True)
        policy_ok = receipt["checks"]["policy"]["pass"]
        tests = receipt["checks"]["tests"]
        tests_ok = (not tests["ran"]) or (tests.get("exit_code") == 0 and not tests.get("timed_out"))
        return 0 if policy_ok and tests_ok else 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
