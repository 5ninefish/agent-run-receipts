from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from arr.receipt import emit_receipt


def _path(value: str | None) -> Path | None:
    return Path(value) if value else None


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="arr",
        description="Emit a verifiable receipt for one agent-produced change.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    emit = sub.add_parser("emit", help="hash inputs, check policy, optionally run tests")
    emit.add_argument("--diff", required=True, help="unified diff file")
    emit.add_argument("--transcript", help="agent transcript / tool log")
    emit.add_argument("--policy", help="JSON policy file (default built-in deny list)")
    emit.add_argument("--test-cmd", help="command whose exit code is recorded")
    emit.add_argument("--run-tests", action="store_true", help="actually execute --test-cmd")
    emit.add_argument("--cwd", help="working directory for --test-cmd")
    emit.add_argument("--timeout", type=int, default=120)
    emit.add_argument("-o", "--output", help="write receipt JSON here (default stdout)")

    args = p.parse_args(argv)
    if args.cmd == "emit":
        receipt = emit_receipt(
            diff_path=_path(args.diff),
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
        policy_ok = receipt["checks"]["policy"]["pass"]
        tests = receipt["checks"]["tests"]
        tests_ok = (not tests["ran"]) or (tests.get("exit_code") == 0 and not tests.get("timed_out"))
        return 0 if policy_ok and tests_ok else 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
