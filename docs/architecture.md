# Architecture: Planka as shared state, Hermes as orchestration

This document describes the public/sanitized version of the Planka + Hermes Kanban pattern.

## Components

### Planka

Role: human-facing operational state.

Planka is used for:

- task capture;
- prioritization;
- state transitions;
- human review;
- blockers;
- execution comments;
- durable handoff.

It is intentionally boring. That is an advantage. Humans already understand boards, lists, cards, labels, and comments.

### Hermes Kanban

Role: orchestration layer.

Hermes Kanban reads board state, interprets cards as work contracts, and manages the lifecycle:

1. inspect card context;
2. decide if the task is ready;
3. decompose if needed;
4. route to a suitable worker;
5. monitor progress;
6. post heartbeat updates;
7. block when required;
8. verify worker output;
9. reconcile final state;
10. move the card.

### Workers

Role: scoped execution.

Workers can be different models or tools, selected for the work type:

- GPT-5.5 for orchestration, reasoning, synthesis, verification;
- Grok 4.5 for product analysis, broad reasoning, rapid iteration, connected workflows;
- Composer 2.5 for code editing and implementation-style lanes;
- Codex/Cursor-style workers for isolated repo changes.

The specific model is replaceable. The board state remains stable.

### Humans

Role: strategy, prioritization, governance, review.

Humans decide:

- priority;
- scope;
- irreversible actions;
- public output;
- merge/deploy decisions;
- when ambiguity requires product judgment.

## Event flow

```text
1. Human creates or updates a Planka card
2. Card enters an agent-ready list
3. Hermes reads the card
4. Hermes validates scope and permissions
5. Hermes chooses a worker or decomposes into sub-cards
6. Worker executes under constraints
7. Hermes reviews output and runs verification
8. Card moves to Human Review, Blocked, or Done
9. Comments preserve the operational trace
```

## Board as protocol

Columns are not decoration. They define the operational protocol.

Recommended baseline:

```text
Backlog
To Do — Human
To Do — Agent
Worker / In Progress
Human Review
Blocked
Done
```

Optional specialized lanes:

```text
Research
Implementation
Verification
Codex Lane
Deployment Approval
```

## Permission boundaries

A mixed human/AI todo manager needs permissions as much as it needs tasks.

Examples of safe autonomous actions:

- inspect files;
- summarize context;
- propose a plan;
- run read-only diagnostics;
- prepare a diff in an isolated branch;
- run tests;
- write an audit comment.

Examples that usually need human review:

- deploy;
- merge;
- delete data;
- publish externally;
- spend money;
- send messages as the user;
- modify secrets or infrastructure;
- trigger irreversible downloads/actions.

## Durable evidence

A card is not complete because an agent says it is complete. It is complete when the card contains evidence:

- changed files;
- commands run;
- test output;
- screenshots/log links;
- deployment URL;
- known risks;
- residual work.

## Why this matters

Chat is good for input. It is weak as a system of record.

Boards provide:

- shared memory;
- visible queueing;
- handoff;
- auditability;
- human override;
- agent coordination.

The best interface for agents may not be another chatbot. It may be the same operational surface where humans already manage work.
