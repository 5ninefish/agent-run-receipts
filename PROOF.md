# Agent Run Receipts — 7–10 day proof

Locked 2026-08-12 from Quick Council + 2026-08-07/08 discovery reframe.
Not a company thesis. A cheap, killable test.

## Artifact (this week)

Ship a small open-source CLI + GitHub Action that emits one receipt per agent change.

In-repo now:

- `python3 -m arr emit` (stdlib)
- `action.yml`
- fixture tests in `tests/test_receipt.py`
- first real receipts emitted from existing brokered-trial agent diffs (local, not published until Dalen says go)

Not in week-1:

- hosted product
- judge panel inside the receipt (optional later)
- CISO / EU-AI-Act positioning
- cold outbound

## Audience

Shops already using Cursor / Claude Code / Codex who merge agent PRs and currently have no inspectable evidence object.

Reach without cold outbound:

1. Public writeup on what receipts show that scanners miss
2. Post to OWASP GenAI / MLSecOps / AI Village / HN / agent-builder Discords
3. GitHub repo as the owned channel
4. Run receipts on 25–50 real agent-generated diffs (brokered-trial corpus first, then public PRs)

## Pre-registered kill (30 days from public publish)

Kill if **any** of:

1. Fewer than **10 teams** try it on **private** repos
2. Fewer than **3** agree to pay or deposit for a hosted version
3. Inbound is all "cool research" with **no** workflow-integration asks
4. Positioning slides into **"Snyk but smaller"**
5. Closing a deal requires **SOC2 / procurement / legal-assurance** selling

Clock started **2026-08-13** on public publish of
`https://github.com/5ninefish/agent-run-receipts`.
Kill check: 2026-09-12.

## Success (does not auto-promote to a company)

- ≥10 private-repo trials **and**
- ≥1 concrete "we want this in CI / merge gate" ask **and**
- still not a scanner

Then: human gate on whether to spend another 14 days on GitHub Action polish + a one-page technical report. Still not a company.

## Day plan

| Day | Done when |
|---|---|
| 1 (today) | CLI + tests + proof file + first receipts on local agent diffs |
| 2–3 | Git init in `/Users/dalen/Public/agent-run-receipts`, public repo only after Dalen says publish |
| 4–6 | Receipts on 25–50 agent diffs; one technical note: what a receipt records that a scanner comment does not |
| 7–10 | Action installable from the public repo; post to the channels above; start the 30-day clock |

## Explicit non-goals

Do not build weekly scanners, dashboards, or a Dbrain LaunchAgent around this during the proof.
