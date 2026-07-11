# Planka + Hermes Kanban + Obsidian

A practical operating system for human/agent project work.

The goal of this repo is simple: a human and an AI agent should be able to open it and understand, step by step, how to run work through **Planka**, **Hermes Kanban**, and **Obsidian**, and why each layer exists.

```text
Chat
  quick human input and notifications
      ↓
Planka
  shared operational truth: cards, status, blockers, evidence
      ↓
Hermes Kanban
  agent orchestration: lifecycle, routing, review gates
      ↓
AI workers
  scoped execution under the card contract
      ↓
Verification
  tests, diffs, logs, screenshots, human approval
      ↓
Obsidian
  long-term project memory: decisions, recaps, roadmap, architecture
```

## Why this exists

Most agent workflows fail because the agent and the human do not share durable state.

Chat is fast, but it is a poor source of truth. It loses context, mixes decisions with noise, and makes it hard to know what is blocked, done, or waiting for review.

Planka gives both sides the same operational board. Hermes Kanban turns cards into executable work contracts. Obsidian keeps the high-level project memory without becoming a task log.

## What each layer owns

### Chat

Use chat for quick task intake, notifications, questions, approval requests, and short status updates.

Do not use chat as the canonical task database.

### Planka

Use Planka for operational truth:

- projects;
- boards;
- lists;
- cards;
- labels;
- blockers;
- review status;
- evidence comments;
- final state.

Planka answers: **what is happening now, who owns it, and what proves it?**

### Hermes Kanban

Use Hermes Kanban as the orchestration layer:

- mirror Planka cards into agent-readable tasks;
- route cards to the correct worker lane;
- enforce lifecycle states;
- prevent silent completion;
- require verification evidence;
- sync final status back to Planka.

Hermes answers: **what should the agent do next, under which constraints, and when is it allowed to move the card?**

### AI workers

Use workers for scoped execution: inspect, implement, test, audit, collect proof, and prepare handoff notes.

Workers do not own truth. They produce evidence.

### Obsidian

Use Obsidian for long-term memory:

- project narrative;
- decisions;
- roadmap changes;
- weekly/monthly recaps;
- architecture notes;
- lessons learned;
- links to important cards, PRs, releases, and docs.

Obsidian answers: **what changed over time, and why did we make these decisions?**

## Step-by-step implementation

Follow these in order. Each step has a reason and a verification check.

### 1. Create one Planka project per real project

**Human:** create or choose the project in Planka.

**Agent:** do not invent project names. Use the existing human-facing name.

**Why:** projects are the first boundary that prevents unrelated work from mixing.

**Verify:** every active product/service has one Planka project.

### 2. Create one board per project

**Human:** keep the board name obvious.

**Agent:** bind work to the matching board, not to a global backlog.

**Why:** agents need a stable scope before they can decide what files, services, and priorities matter.

**Verify:** no project work is tracked only in chat.

### 3. Use a standard board lifecycle

Recommended lists:

```text
Inbox
Ready for Agent
In Progress
Blocked
Review Required
Done
Archived
```

**Human:** move cards into `Ready for Agent` only when they are actionable.

**Agent:** only pick cards from the agreed intake lane.

**Why:** lifecycle states make automation predictable. The agent should never guess whether a card is ready.

**Verify:** every board uses the same list names or a documented equivalent.

### 4. Write cards as work contracts

A card should contain objective, context, relevant paths/links, constraints, acceptance criteria, permission boundaries, verification requirements, and latest human decision.

**Human:** write the outcome and constraints.

**Agent:** normalize vague cards before execution by commenting what is missing or moving the card to `Blocked`.

**Why:** a card is not a reminder. It is the execution contract.

**Verify:** an agent can answer “what do I need to do, what must I not do, and how do I prove completion?” from the card alone.

See [`examples/card-contract.md`](examples/card-contract.md).

### 5. Mirror Planka into Hermes Kanban

**Human:** keep using Planka as the visible board.

**Agent/operator:** run a deterministic bridge that reads Planka cards and creates/updates matching Hermes Kanban tasks.

**Why:** Planka is human-friendly. Hermes Kanban is agent-native. The bridge lets each side use the right interface without splitting truth.

**Verify:** a card moved to `Ready for Agent` appears as one matching Hermes task with the same project, title, state, and source link.

### 6. Let Hermes route the work

**Human:** do not assign implementation details unless needed.

**Agent:** Hermes selects the worker lane, passes the card contract, and keeps lifecycle ownership.

**Why:** workers are replaceable. The orchestrator must keep the durable state and review gate.

**Verify:** worker output is attached to the task/card as evidence, not lost inside a private session.

### 7. Require evidence before review

**Agent:** before moving to `Review Required`, attach evidence such as tests run, diff summary, screenshots, logs, URLs checked, known risks, and remaining manual steps.

**Human:** review evidence, not just a completion claim.

**Why:** “done” without evidence is not operational state.

**Verify:** every `Review Required` card contains enough information for another person or agent to audit it.

### 8. Sync final status back to Planka

**Agent/operator:** when Hermes marks a task done, blocked, or needing review, update the Planka card and add a concise comment.

**Why:** Planka must remain the shared operational truth. If the agent only updates its own queue, the human board becomes stale.

**Verify:** Planka and Hermes show the same state for the same card.

### 9. Write only high-level memory to Obsidian

**Agent/operator:** sync summaries, decisions, final delivery notes, and roadmap-level blockers into Obsidian.

**Do not sync:** every heartbeat, every command, every transient log, every raw worker message.

**Why:** Obsidian is long-term project memory. If it becomes a log stream, it stops being useful.

**Verify:** an Obsidian project note explains direction, decisions, risks, and important links without duplicating the whole board.

See [`docs/04-obsidian-memory-layer.md`](docs/04-obsidian-memory-layer.md).

## Minimal repository map

```text
README.md
  start here: full operating model and step-by-step setup

docs/01-system-model.md
  responsibilities of Chat, Planka, Hermes Kanban, workers, verification, Obsidian

docs/02-step-by-step-implementation.md
  implementation checklist with human actions, agent actions, reasons, and checks

docs/03-agent-operating-protocol.md
  rules an agent should follow while working from cards

docs/04-obsidian-memory-layer.md
  how to sync project memory without creating noise

examples/card-contract.md
  copy/paste card template

examples/board-lifecycle.md
  recommended Planka lists and state transitions
```

## Done criteria for an implementation

A Planka + Hermes + Obsidian setup is working when:

- a human can create a card in Planka;
- Hermes Kanban sees the card once;
- an agent can execute from the card contract;
- evidence is posted before review;
- final status syncs back to Planka;
- Obsidian receives only durable project memory;
- another human or agent can audit what happened later.

## License

MIT.
