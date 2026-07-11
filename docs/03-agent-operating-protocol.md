# 03 — Agent operating protocol

These are the rules an AI agent should follow when working from Planka through Hermes Kanban.

## 1. Treat the card as the contract

Before starting, read title, description, comments, labels, checklist, linked files or URLs, acceptance criteria, and permission boundaries.

If the card is too vague, do not guess. Ask for clarification or mark it blocked with the missing fields.

## 2. Preserve source identity

Every Hermes Kanban task created from Planka should keep a stable source reference:

```text
planka:<card_id>
```

**Reason:** without a stable source key, sync jobs create duplicates.

## 3. Use lifecycle states strictly

Suggested mapping:

```text
Planka: Ready for Agent    → Hermes: ready
Planka: In Progress        → Hermes: in_progress
Planka: Blocked            → Hermes: blocked
Planka: Review Required    → Hermes: review-required
Planka: Done               → Hermes: done
```

The agent should not invent new states during execution.

## 4. Keep progress concise

Good progress comment:

```text
Checked repo state. Found failing auth test in tests/auth.test.ts. Next: patch callback validation and rerun targeted tests.
```

Bad progress comment:

```text
I am now thinking about possible reasons this might happen...
```

**Reason:** comments are operational evidence, not a transcript of the agent’s thoughts.

## 5. Block safely

Move to blocked when credentials are missing, the task requires a human decision, permissions are unclear, acceptance criteria conflict, the environment cannot reproduce the issue, or the next action is destructive and not approved.

A blocker comment must include:

- what stopped the work;
- what was already tried;
- the exact decision or input needed.

## 6. Never mark done without evidence

Before `Review Required` or `Done`, attach at least one of:

- test command and result;
- diff summary;
- screenshot path or URL;
- deploy URL checked;
- log excerpt;
- audit finding;
- explicit “not testable because…” note.

## 7. Separate execution from approval

The agent may execute scoped work inside the permission boundary.

The agent should ask for human approval before merge, deploy, destructive data changes, public posting, credential changes, repository visibility changes, or deleting production resources.

## 8. Write the final handoff

A final handoff should include:

```text
Summary:
- What changed

Evidence:
- Tests / logs / screenshots / URLs

Risks:
- Known limitations or follow-up

Next decision:
- What the human needs to approve, if anything
```

**Reason:** the next human or agent should be able to continue without reading the original session.
