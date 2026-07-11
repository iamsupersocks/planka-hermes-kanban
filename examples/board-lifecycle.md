# Example: board lifecycle protocol

A kanban board for mixed human/AI work should model operational states, not just vibes.

## Baseline lists

```text
Backlog
To Do — Human
To Do — Agent
Worker / In Progress
Human Review
Blocked
Done
```

## List semantics

### Backlog

Ideas, requests, or incomplete tasks. Agents should not start from here unless explicitly asked to triage.

### To Do — Human

Tasks requiring human action, context, product judgment, or approval.

### To Do — Agent

Tasks ready for Hermes Kanban to pick up or delegate.

A card in this list should have enough context and acceptance criteria to run safely.

### Worker / In Progress

A human or agent is actively working.

Expected behavior:

- card owner is visible;
- heartbeat comments appear during long work;
- no second worker starts without coordination.

### Human Review

The agent prepared something but needs a human decision.

Examples:

- approve deployment;
- choose among release candidates;
- validate copy/design;
- approve destructive operation;
- merge PR.

### Blocked

The task cannot progress.

A blocked card must include:

- what was attempted;
- exact blocker;
- who/what can unblock;
- safe next step.

### Done

Work is complete and verified.

Done cards should include evidence, not just a completion claim.

## Optional labels

```text
Needs Approval
Safe Autonomous
Destructive
Public Output
Credential Needed
Repo Dirty
Needs Verification
```

## Operational rule

If a card cannot be resumed by a different human or agent from the visible card state, the workflow is not sufficiently documented.
