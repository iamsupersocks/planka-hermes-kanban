# Planka + Hermes Kanban

An open pattern for using a human kanban board as shared operational state for AI agents.

This repository documents a practical architecture where **Planka** is the human-facing source of truth and **Hermes Kanban** is the orchestration layer behind the board. Cards become executable work contracts: humans can create, prioritize, review, and unblock them; agents can read them, execute scoped work, post evidence, block safely, and hand off.

The human does not need to live inside Planka. In a real deployment, the daily cockpit can be Telegram, Discord, Slack, or another chat surface. The important invariant is that tracked work is mirrored back into Planka so the board remains the canonical state.

The core idea:

> AI agents need shared state, not another chat UI.

## Architecture

```text
Human operators
  ask, prioritize, review, approve
        │
        ▼
Chat cockpit
  Telegram / Discord / Slack
  fast input + notifications
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
        │
        ▼
Obsidian / long-term project memory
  high-level recaps, decisions, roadmap narrative
```

## What this repo contains

- [`docs/article-fr.md`](docs/article-fr.md) — long-form French article draft.
- [`docs/x-thread-fr.md`](docs/x-thread-fr.md) — X/Twitter thread draft.
- [`docs/architecture.md`](docs/architecture.md) — sanitized architecture notes.
- [`docs/operating-loop.md`](docs/operating-loop.md) — chat → Planka → Hermes → worker → verification loop.
- [`docs/obsidian-project-tracking.md`](docs/obsidian-project-tracking.md) — high-level project memory layer.
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

## Three-layer operating system

```text
Chat = cockpit
Planka = operational state
Obsidian = high-level project memory
```

Chat is for fast human input and notifications. Planka is for current truth: active work, blockers, evidence, review, and done/block state. Obsidian is for the slower layer: project narrative, major decisions, roadmap themes, recaps, and lessons learned.

If the chat layer bypasses Planka, the system loses shared state. If Planka tries to replace Obsidian, the long-term project memory becomes too noisy. The layers should sync selectively, not collapse into each other.

## Status

This is a public write-up of an evolving internal pattern. It deliberately avoids private infrastructure details, secrets, credentials, private board IDs, and project-specific operational data.

## License

MIT for the text and examples unless otherwise stated.
