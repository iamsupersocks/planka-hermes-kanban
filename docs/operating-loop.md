# Operating loop: chat cockpit, board state, agent execution

The useful pattern is not “humans must live in Planka”. The board is the canonical state, but the human cockpit can be Telegram, Discord, Slack, or another chat surface.

A practical loop looks like this:

```text
Human
  asks, corrects, approves, prioritizes
        │
        ▼
Chat cockpit
  Telegram / Discord / Slack
  fast input, questions, notifications
        │
        ▼
Board adapter
  creates or updates the right Planka card
  resolves project, board, list, owner, acceptance criteria
        │
        ▼
Planka
  visible operational state
  roadmap, current status, blockers, evidence
        │
        ▼
Hermes Kanban
  execution graph, idempotency, worker dispatch, audit trail
        │
        ▼
Worker lane
  model/tool/repo-specific execution
        │
        ▼
Parent Hermes review
  independent verification, tests, diffs, screenshots, risk notes
        │
        ▼
Planka + chat return
  card comment/status is updated, human receives the useful summary
```

## Why systems stop using Planka systematically

This usually happens for operational reasons rather than product reasons:

1. **Chat is faster than board entry.** Humans naturally send a message instead of opening the board. The fix is an intake bridge, not forcing the human into Planka.
2. **The bridge is paused or partial.** If the Planka → Hermes dispatcher or Hermes → Planka watcher is disabled, agents fall back to hidden chat/session state.
3. **The board is treated as reporting, not control.** If cards are updated after the fact, Planka becomes a dashboard instead of the workflow state machine.
4. **No project resolver.** The intake layer must decide which project/board/card owns a request. Without that, agents avoid writing to the board because the target is ambiguous.
5. **No canary discipline.** Moving many cards into an automation lane is risky. The correct pattern is one canary card end-to-end, then a bounded batch.
6. **Human review is underspecified.** Some actions need approval: deploy, merge, publish, spend money, delete data, send messages. The board must make those gates visible.

## Required invariants

- A tracked work item has one canonical card.
- The card links to the Hermes Kanban task or execution run.
- Agent work starts only after the card is in an execution-ready state.
- Long work posts heartbeat comments.
- Completion requires evidence, not a claim.
- If the user talks in chat, the board is still updated behind the scenes.
- If the board changes, the chat cockpit can notify the human.

## Implementation note

For a private deployment, two automations are enough to make the loop real:

1. **Intake / dispatcher:** chat or Planka `To Do — Agent` → Hermes Kanban task.
2. **Watcher / reporter:** Hermes Kanban status and evidence → Planka comment/status → chat notification.

Both should be deterministic scripts where possible. The LLM should reason about scope and verification; it should not be the polling daemon.