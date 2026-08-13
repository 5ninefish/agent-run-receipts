# Agent Run Receipts

A vendor-neutral **evidence object** for one agent-produced source change.

It answers:

> What evidence accompanied this change, what did that evidence say, and has the recorded evidence changed since the receipt was created?

It does **not** answer: “was the agent good,” “was the agent fully constrained,” or “who signed this.”

```
CHANGE → AGENT EVIDENCE (hashed) → POLICY CHECKS (facts) → TEST EVIDENCE → RECEIPT
```

Not a scanner. Not SLSA. Not GitHub Copilot’s vendor log. Those already exist. This is one portable JSON object Cursor / Claude Code / Codex / Grok / Copilot can all emit.

## Claims v0 actually makes

- The supplied diff / transcript / policy / test command were hashed.
- These **factual** checks against the supplied artifacts: denied paths in the diff, secret-like regex hits, test requested/executed/exit code.
- `receipt_sha256` lets you see if **this receipt file** was altered later.

## Claims v0 does not make

- The transcript is complete (`transcript.complete` is always `unknown`).
- The agent did nothing unrecorded (it cannot know).
- SHA-256 identifies the author.
- Policy PASS means runtime enforcement, unless ARR actually saw the artifact (e.g. the diff contains `.env`).

Raw transcripts and test logs stay off the receipt. Only hashes and derived facts go in. The org keeps the private files.

## You do not run this by hand

Copy [`examples/install-on-your-repo.yml`](examples/install-on-your-repo.yml) to `.github/workflows/agent-run-receipt.yml`. Every pull request gets a receipt.

```bash
PYTHONPATH=. python3 -m arr emit --diff examples/ok.diff --transcript examples/transcript.txt --policy examples/policy.json
PYTHONPATH=. python3 -m arr emit --from-git HEAD
```

Exit `0` = supplied-artifact policy checks passed (and tests passed if `--run-tests`). Exit `2` = a recorded check failed.

## What this will not become

- Snyk / an AI code reviewer / an AI governance suite / a compliance platform
- Sigstore / GitHub App / hosted dashboard — not until reality votes (see [PROOF.md](PROOF.md))

SBOM does not tell you if software is good. A receipt does not tell you if an agent change is good. It records what evidence accompanied the run.

## Proof

[PROOF.md](PROOF.md). Clock started 2026-08-13. Kill check 2026-09-12.

## License

MIT
