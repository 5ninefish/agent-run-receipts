# Launch copy — paste when you are ready

Do not auto-post. Dalen (or an agent he tells to post) pastes these.

## GitHub repo description

Tamper-evident receipts for one agent-produced code change. Not a scanner. Install a GitHub Action; every PR gets a receipt.

## Short X / LinkedIn

Coding agents now write real pull requests. Teams still merge on vibe.

Agent Run Receipts is a paper trail for one agent change: the diff, the policy check, the tests, a fingerprint.

You don’t run it. A GitHub Action emits a receipt on every PR.

30-day experiment. If people don’t use it on private repos, it dies.

https://github.com/5ninefish/agent-run-receipts
https://5ninefish.github.io/agent-run-receipts/

## Hacker News (title)

Show HN: receipts for AI-written pull requests (not another scanner)

## Hacker News (text)

Agents (Cursor, Claude Code, Codex, etc.) now open real PRs. The merge decision is usually a chat summary or a scanner badge. Those are not a record of what was checked.

This is a tiny CLI + GitHub Action. On every PR it hashes the diff, runs a deny-list policy, optionally records tests, and comments a receipt fingerprint. Change the patch later and the hash no longer matches.

It is deliberately not Snyk, not EU AI Act paperwork, not a hosted platform. 30-day public experiment with a pre-registered kill bar in the repo.

https://github.com/5ninefish/agent-run-receipts

## Discord / OWASP / agent-builder (one paragraph)

Looking for shops already merging Cursor/Claude Code/Codex PRs. We shipped a receipt object (diff + policy + tests + hash) that posts on the PR automatically. If you try it on a *private* repo this month and tell us whether you want it as a merge gate, that is the whole experiment. Not a scanner.

## What we are not doing this week

Standing social-media autopilot, a marketing site CMS, or scheduled posting. No X/Twitter API is provisioned. The website for this experiment is the GitHub Pages page above. A real PeakForge site + social system is a later incubator item, not this proof.
