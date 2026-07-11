# Example card contract

Use this as the body of a Planka card that should be executable by an agent.

```markdown
## Objective
Describe the outcome in one or two sentences.

## Context
Explain why this matters and what the agent should know before starting.

## Scope
The agent may:
- ...

The agent must not:
- ...

## Relevant links / paths
- Repository:
- Files:
- Service URL:
- Existing docs:

## Acceptance criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Verification required
The agent must provide:
- command output or test result;
- screenshots or URL checks if UI is involved;
- diff summary if files changed;
- risk/follow-up note if anything remains.

## Human approval required before
- merge;
- deploy;
- deleting data;
- changing credentials;
- public posting;
- other high-impact action.

## Latest human decision
YYYY-MM-DD — Decision — reason.
```

## Why this format works

The card gives the agent enough structure to execute without inventing scope.

It also gives the human a review checklist: if the acceptance criteria and verification evidence are missing, the card is not ready to be marked done.
