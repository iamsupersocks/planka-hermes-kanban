# Example board lifecycle

Use the same lifecycle across boards unless you have a documented reason not to.

```text
Inbox
Ready for Agent
In Progress
Blocked
Review Required
Done
Archived
```

## Inbox

Raw intake.

Use for ideas, notes, vague requests, and tasks that are not ready for execution.

Agent rule: do not execute from this lane unless explicitly instructed.

## Ready for Agent

Actionable work.

A card can enter this lane when it has:

- objective;
- context;
- acceptance criteria;
- permission boundary;
- verification requirement.

Agent rule: this is the normal intake lane.

## In Progress

A worker is actively executing.

Agent rule: post concise progress when the state changes or evidence is produced.

## Blocked

Work cannot continue safely.

A blocked card must say:

- what is blocked;
- what was tried;
- what input or decision is needed.

Agent rule: blocking is better than guessing.

## Review Required

Execution is complete enough to inspect.

A review card must include evidence:

- tests;
- logs;
- screenshots;
- URLs;
- diff summary;
- known risks.

Human rule: review the evidence, then approve, reject, or request changes.

## Done

The work is accepted.

Done means:

- acceptance criteria satisfied;
- evidence attached;
- human approval obtained when required;
- final status synced.

## Archived

Historical work that should not clutter active operations.

Agent rule: do not resurrect archived cards without a human signal.
