# Agent Run Receipts

A CLI / GitHub Action that takes an agent's **diff + transcript + policy + test command** and emits a **verifiable receipt**: what was checked, whether policy passed, whether tests ran, and tamper-evident SHA-256 hashes of every input.

This is **not** a security scanner and **not** an EU AI Act / CISO product. Scanners ask "does this look dangerous?" Receipts ask "what evidence exists that this agent change was inspected, constrained, and tested?"

```
diff + transcript + policy + optional tests
        │
        ▼
   arr emit
        │
        ▼
receipt.json  (content-addressed; receipt_sha256 covers the body)
```

## Why this exists

Coding agents now produce real pull requests. Teams still merge on vibe, a scanner badge, or a chat summary. Those are not the same artifact. A receipt is a small, inspectable record another human or later agent can re-hash.

Day-1 scope is deliberately narrow. Judges, hosted SaaS, and procurement theater are out of v0.

## Install

```bash
# from this directory, no extra deps
PYTHONPATH=. python3 -m arr emit --diff examples/ok.diff --transcript examples/transcript.txt --policy examples/policy.json
```

Or:

```bash
pip install -e .
arr emit --diff examples/ok.diff -o receipt.json
```

Exit `0` = policy passed (and tests passed if `--run-tests`). Exit `2` = policy failed or tests failed.

## GitHub Action

```yaml
- uses: 5ninefish/agent-run-receipts@v0
  with:
    diff: agent.patch
    transcript: agent.transcript.md
    policy: policy.json
    test_cmd: pytest -q
    run_tests: "true"
    output: agent-run-receipt.json
```

## What v0 records

- SHA-256 and byte length of the diff, transcript, and policy
- SHA-256 of the test command string
- Changed paths parsed from a unified diff
- Policy pass/fail + violation list (deny path globs, deny regexes, max diff size)
- Optional test run: exit code, timeout flag, stdout/stderr hashes (not the raw logs)
- `receipt_sha256` over the canonical JSON body (that field itself excluded)

## What v0 will not become

- Snyk / SkillSpector / Aguara Watch
- SOC2 or EU AI Act compliance paperwork
- A CISO sales motion
- A hosted platform until the 30-day kill bar says people actually use the CLI

## Proof protocol

See [PROOF.md](PROOF.md). Pre-registered kill: in 30 days, fewer than 10 teams try it on private repos, **or** fewer than 3 will pay/deposit for hosted, **or** inbound is all "cool research," **or** it becomes "Snyk but smaller."

## License

MIT
