# Planka + Hermes Kanban

An open pattern for using a human kanban board as shared operational state for AI agents.

This repository documents a practical architecture where **Planka** is the human-facing source of truth and **Hermes Kanban** is the orchestration layer behind the board. Cards become executable work contracts: humans can create, prioritize, review, and unblock them; agents can read them, execute scoped work, post evidence, block safely, and hand off.

The core idea:

> AI agents do not need another chat UI. They need shared operational state with humans.

## Architecture

```text
Human operators
  create, prioritize, review, approve
        │
        ▼
Planka
  projects, boards, lists, cards, comments, labels
  = shared state + audit trail + work contract
        │
        ▼
Hermes Kanban
  orchestrates card lifecycle, decomposition, assignment,
  worker routing, heartbeats, blockers, reconciliation
        │
        ▼
AI workers
  GPT-5.5 / Grok 4.5 / Composer 2.5 / Codex-style lanes
  execute scoped work under card constraints
        │
        ▼
Verification + handoff
  tests, diffs, logs, screenshots, human review, done/block
```

## What this repo contains

- [`docs/article-fr.md`](docs/article-fr.md) — long-form French article draft.
- [`docs/x-thread-fr.md`](docs/x-thread-fr.md) — X/Twitter thread draft.
- [`docs/architecture.md`](docs/architecture.md) — sanitized architecture notes.
- [`docs/skill-analysis.md`](docs/skill-analysis.md) — analysis of the Hermes Kanban operating model.
- [`examples/card-contract.md`](examples/card-contract.md) — example card format.
- [`examples/board-lifecycle.md`](examples/board-lifecycle.md) — suggested list/column protocol.

## Why Planka?

Planka is simple enough for humans and structured enough for agents:

- projects;
- boards;
- lists;
- cards;
- descriptions;
- comments;
- labels;
- assignments;
- history.

That is enough to model work as durable shared state. The board remains understandable to humans while becoming machine-actionable for agents.

## The card contract

A card is not just a reminder. It is the unit of delegation.

A good agent-readable card contains:

- objective;
- context;
- relevant paths/services/links;
- constraints;
- acceptance criteria;
- permission boundaries;
- verification requirements;
- latest human decisions;
- blocker history.

## Operating principle

Hermes owns the lifecycle. Workers execute.

A worker may inspect files, draft changes, run tests, or produce an audit. Hermes Kanban remains responsible for deciding when a card moves, when a blocker is valid, and whether the final state has been verified.

This avoids a common failure mode of agent workflows: a worker claims completion without durable evidence or human-readable handoff.

## Status

This is a public write-up of an evolving internal pattern. It deliberately avoids private infrastructure details, secrets, credentials, private board IDs, and project-specific operational data.

## License

MIT for the text and examples unless otherwise stated.
