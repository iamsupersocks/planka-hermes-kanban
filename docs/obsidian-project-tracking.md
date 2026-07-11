# Obsidian high-level project tracking

Planka is the operational board. Obsidian is the high-level project memory.

They should not duplicate each other.

## Split of responsibility

### Planka

Use Planka for live operational state:

- current cards;
- active blockers;
- execution lanes;
- human review;
- evidence comments;
- final task status.

Planka answers: **what is happening now, who owns it, and what evidence proves it?**

### Obsidian

Use Obsidian for durable project understanding:

- project narrative;
- strategy and product decisions;
- weekly/monthly recaps;
- roadmap themes;
- architecture notes;
- lessons learned;
- links to important cards, PRs, docs, and releases.

Obsidian answers: **what does this project mean, what changed over time, and why did we make these decisions?**

## Suggested note structure

```text
Projects/
  Project Name/
    00 Overview.md
    01 Roadmap.md
    02 Decisions.md
    03 Weekly Recaps.md
    04 Architecture.md
    05 Open Questions.md
```

## Project overview template

```markdown
# Project Name

## One-liner
What this project is, in one sentence.

## Current direction
The current strategic direction, not a task list.

## Active workstreams
- Workstream A — status / goal / owner
- Workstream B — status / goal / owner

## Key decisions
- YYYY-MM-DD — Decision — why it was made

## Current risks
- Risk — mitigation / next review point

## Links
- Planka board:
- GitHub repo:
- Production URL:
- Latest recap:
```

## Sync rule

Obsidian should receive summaries, not every heartbeat.

A good sync cadence:

- daily or weekly high-level recap;
- major status changes;
- final delivery summaries;
- decisions and reversals;
- important blockers that change roadmap or priority.

Avoid copying raw operational noise into Obsidian. If everything is mirrored, the vault becomes another log pile.

## Live sync pattern

A conservative Planka/Hermes → Obsidian bridge should run as a deterministic no-agent job:

```text
Planka comments/status changes
→ filter high-level events
→ refresh project snapshot
→ append final/blocker/decision entries
→ stay silent when nothing changed
```

In a public implementation, this can be any small sync script owned by the operator, for example:

```text
planka_obsidian_project_sync.py
```

If your Obsidian vault has a branded/internal name, keep that name private to your deployment. The public pattern only assumes a normal folder of Markdown notes.

The script should write only compact project memory:

- live counts by project/list;
- completed or blocked cards;
- review handoffs;
- comments with evidence, decisions, verification, commit/deploy notes, or durable blockers.

It should not copy every worker heartbeat into Obsidian.

## Public-system takeaway

A strong human/agent operating system has three layers:

```text
Chat cockpit
  fast human input and notifications

Planka
  shared operational state and execution evidence

Obsidian
  high-level project memory and long-term narrative
```

The agent should know which layer it is writing to. A blocker belongs in Planka. A product decision belongs in Obsidian. A short “done / needs review” message belongs in chat.