# 02 — Step-by-step implementation

This checklist is written for both a human operator and an AI agent.

Every step includes what the human does, what the agent does, why the step exists, and how to verify it.

## 1. Define the project boundary

**Human:** choose the project name and scope.

**Agent:** use the human name exactly. Do not create alternate names unless asked.

**Why:** agents need a stable boundary to avoid mixing files, services, and priorities.

**Verify:** the project has one canonical name across Planka, Hermes Kanban, and Obsidian.

## 2. Create the Planka board

**Human:** create one board for the project.

**Agent:** read from this board when looking for work.

**Why:** the board is the current operational truth.

**Verify:** the board exists and has the standard lifecycle lists.

## 3. Add standard lifecycle lists

```text
Inbox
Ready for Agent
In Progress
Blocked
Review Required
Done
Archived
```

**Human:** place new raw ideas in `Inbox` and actionable work in `Ready for Agent`.

**Agent:** only start cards from `Ready for Agent`, unless a different intake lane is documented.

**Why:** predictable lanes let automation run without guessing intent.

**Verify:** an agent can map each Planka list to one Hermes Kanban state.

## 4. Write the first card contract

**Human:** write the objective, acceptance criteria, constraints, and review requirements.

**Agent:** if required fields are missing, comment with the missing information and move/block the card instead of improvising.

**Why:** vague tasks cause agents to overreach or produce unauditable work.

**Verify:** the card answers what outcome is expected, what context matters, what boundaries apply, and how success will be verified.

Use [`../examples/card-contract.md`](../examples/card-contract.md).

## 5. Connect Planka to Hermes Kanban

**Human/operator:** configure a bridge that reads Planka and writes Hermes Kanban tasks.

**Agent:** preserve source identity. A Planka card should map to exactly one Hermes task.

**Why:** duplicate tasks create split-brain state.

**Verify:** moving a card to `Ready for Agent` creates or updates one matching Hermes task.

## 6. Execute through Hermes, not directly from chat

**Human:** ask for work in chat if convenient, but make sure it becomes a card.

**Agent:** if a chat request is real project work, create or update the Planka card before execution.

**Why:** chat-only work disappears from the shared board.

**Verify:** every meaningful work item has a Planka card before or immediately after execution starts.

## 7. Attach evidence during execution

**Agent:** post concise progress and evidence to the task/card: command run, test result, file changed, link checked, blocker found, or decision needed.

**Human:** use evidence comments to review status without reading the agent’s private session.

**Why:** evidence makes the work auditable.

**Verify:** another agent can continue from the card without asking what happened.

## 8. Move to review only when verifiable

**Agent:** move a task to `Review Required` only when evidence exists.

**Human:** approve, reject, or request changes from the evidence.

**Why:** review is the safety gate before done/deploy/merge.

**Verify:** every review card includes test output or a clear reason why no test was possible.

## 9. Sync the result back to Planka

**Agent/operator:** update the Planka card with final state and summary.

**Why:** the human-facing board must not become stale.

**Verify:** Planka and Hermes show the same state.

## 10. Write durable memory to Obsidian

**Agent/operator:** write only the high-level summary: decision made, delivery completed, major blocker, roadmap change, architecture note, or important link.

**Why:** Obsidian is for understanding the project later, not for replaying every command.

**Verify:** the Obsidian project note is readable by a human who did not follow the daily board.
