# 01 — System model

This system has one rule: each layer owns one kind of state.

If two layers try to own the same thing, the workflow becomes noisy and unreliable.

```text
Chat       = fast interaction
Planka     = operational state
Hermes     = orchestration
Workers    = execution
Review     = evidence gate
Obsidian   = long-term memory
```

## Chat

Chat is the cockpit.

Use it for short interactions:

- create this task;
- what is blocked;
- approve this;
- send me the result;
- notify me when review is ready.

Do not use chat as the place where the project state lives.

**Reason:** chat is chronological, noisy, and hard to audit.

## Planka

Planka is the operational source of truth.

It stores projects, boards, cards, lists, labels, comments, blockers, review state, evidence, and final status.

**Reason:** a board gives humans and agents the same view of current work.

## Hermes Kanban

Hermes Kanban is the agent orchestration layer.

It decides:

- which cards are ready;
- which worker should handle them;
- when work is blocked;
- when evidence is sufficient;
- when a card can move to review or done;
- how to reconcile state back to Planka.

**Reason:** workers should not directly own the project lifecycle. They execute; Hermes coordinates.

## AI workers

Workers perform scoped tasks.

They may read files, make changes, run commands, inspect services, draft docs, produce analysis, and collect proof.

They must not silently mark work done without evidence.

**Reason:** a worker session is temporary. The evidence must survive outside the session.

## Verification

Verification is the gate between “agent says it is done” and “the system accepts it”.

Evidence can include command output, test results, browser checks, screenshots, logs, commits, deploy URLs, and manual review notes.

**Reason:** review should be based on artifacts, not trust.

## Obsidian

Obsidian is the durable project memory.

It stores decisions, recaps, roadmap changes, architecture notes, lessons learned, and links to important cards or PRs.

**Reason:** Planka is for the live board. Obsidian is for understanding the project over time.
