# Skill analysis: Hermes Kanban operating model

This is a public, sanitized analysis of the Hermes Kanban operating model used behind Planka.

## 1. Kanban is used when work needs durable state

The key trigger is not “task management” in the abstract. Kanban becomes useful when work is:

- parallel;
- multi-step;
- long-running;
- shared between humans and agents;
- dependent on review or credentials;
- risky enough to require a visible audit trail.

For small one-shot tasks, chat is fine. For work that needs continuity, the board becomes the state machine.

## 2. Orchestrator and worker are separate roles

The operating model distinguishes two roles:

### Orchestrator

The orchestrator owns the lifecycle:

- decompose tasks;
- create cards;
- assign workers;
- monitor state;
- reconcile results;
- enforce blocking rules;
- verify completion.

### Worker

The worker owns scoped execution:

- claim or receive a card;
- inspect context;
- perform the task;
- post updates;
- stop when blocked;
- produce a completion report.

This separation matters. If the worker is allowed to declare its own work complete without verification, the board becomes performative rather than operational.

## 3. The card is the source of truth

Workers should treat the card as canonical context.

A worker should inspect:

- description;
- acceptance criteria;
- linked comments;
- current list/status;
- labels and assignees;
- recent blocker notes;
- human decisions.

This reduces “agent drift”, where an agent continues based on stale chat context after the board has changed.

## 4. Heartbeats are short operational comments

Useful heartbeat comments answer:

- what is being worked on;
- what was inspected;
- what changed;
- what command/test ran;
- what is next;
- what is blocked.

Bad heartbeat comments are vague:

- “Working on it”;
- “Almost done”;
- “Fixed issues”;
- “Implemented improvements”.

A good heartbeat is enough for a human or another agent to resume.

## 5. Blocking is a first-class outcome

A blocked card is not a failure. It is a correct state transition when the system lacks what it needs.

Good block reasons include:

- what was attempted;
- exact error or missing requirement;
- who/what can unblock it;
- whether partial work is safe to keep;
- recommended next action.

Agents should block fast rather than hallucinating progress.

## 6. Codex/Composer-style lanes are subordinate implementation lanes

For code work, a worker such as Codex, Composer, Cursor, or another coding agent can run as an implementation lane.

Pattern:

1. Hermes creates a self-contained prompt from the card.
2. The coding worker operates in an isolated branch/worktree when needed.
3. The worker returns a diff and report.
4. Hermes reviews the diff and reruns verification.
5. Hermes updates the card.

The coding worker should not directly mark the Kanban task complete. That remains the orchestrator’s job.

## 7. Direct board updates require safety rules

When updating Planka directly, the safe sequence is:

1. read first;
2. identify exact project/board/list/card IDs;
3. write minimally;
4. add audit trail where required;
5. re-query to verify visible state;
6. stop if a safety layer blocks the write.

Public takeaway: an AI operating a task board must treat board writes as real side effects, not as harmless UI manipulation.

## 8. Completion requires evidence

A card should only move to Done after evidence exists.

Examples:

- build/test command with exit code;
- before/after screenshots;
- commit or PR link;
- deployed URL;
- queue/job status;
- manual verification note;
- known risks.

This is where many agent systems fail: they optimize for claiming completion, not proving completion.

## 9. Chat mirrors are optional, not canonical

Discord, Telegram, Slack, or X can be used as cockpits:

- create cards from messages;
- notify blockers;
- broadcast summaries;
- ask for approvals.

But the board remains canonical.

A chat thread should not replace the card state. Otherwise the workflow becomes fragmented again.

## 10. The product insight

The strongest product idea is not “AI inside a kanban board”.

It is:

> A todo manager where each unit of work is simultaneously human-readable and agent-executable.

That requires:

- structured context;
- state transitions;
- permission boundaries;
- durable evidence;
- human review;
- model/tool routing;
- handoff between humans and agents.

Planka + Hermes Kanban is one concrete implementation of that pattern.
