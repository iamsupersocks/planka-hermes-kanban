# 04 — Obsidian memory layer

Obsidian is the high-level project memory.

It should not duplicate Planka. It should explain what matters over time.

## What belongs in Obsidian

Write to Obsidian when something changes the understanding of the project:

- a product decision;
- an architecture decision;
- a completed milestone;
- a major blocker;
- a roadmap change;
- a useful lesson learned;
- a release summary;
- links to important cards, PRs, docs, and deployments.

## What does not belong in Obsidian

Do not sync:

- every worker heartbeat;
- every command output;
- raw logs;
- duplicate card descriptions;
- temporary errors that were resolved immediately;
- private agent scratchpad text;
- noisy status chatter.

**Reason:** if Obsidian becomes a log pile, humans stop reading it.

## Suggested vault structure

```text
Projects/
  Project Name/
    00 Overview.md
    01 Roadmap.md
    02 Decisions.md
    03 Recaps.md
    04 Architecture.md
    05 Open Questions.md
```

## Project overview template

```markdown
# Project Name

## One-liner
What this project is, in one sentence.

## Current direction
The current strategic direction.

## Active workstreams
- Workstream — status / owner / next review point

## Key decisions
- YYYY-MM-DD — Decision — why it was made

## Current risks
- Risk — mitigation / next review point

## Links
- Planka board:
- Repository:
- Production URL:
- Latest recap:
```

## Sync pattern

A conservative Planka/Hermes to Obsidian sync should be deterministic and quiet when nothing important changed.

```text
Planka/Hermes events
  ↓
filter durable events only
  ↓
update project snapshot
  ↓
append decision/blocker/delivery recap
  ↓
stay silent if no durable event exists
```

## Durable event examples

Sync this:

```text
2026-07-11 — Authentication refactor completed.
Evidence: tests/auth.test.ts passed, login smoke test passed.
Decision: keep OAuth callback validation server-side.
Links: Planka card, PR, deploy URL.
```

Do not sync this:

```text
Agent started task.
Agent opened file.
Agent is thinking.
Agent ran command.
Agent fixed typo.
```

## Verification

An Obsidian project note is healthy when a new human can answer:

- what is this project;
- where is it going;
- what changed recently;
- what decisions shaped it;
- where to inspect operational proof.
