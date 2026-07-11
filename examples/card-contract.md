# Example: agent-readable card contract

```markdown
## Objective

Fix mobile readability issues on the `/dashboard` page.

## Context

- Repo: `~/example-app`
- Page: `/dashboard`
- Priority: mobile first
- Known issue: horizontal overflow on 390px width
- Do not refactor unrelated layout components

## Acceptance criteria

- [ ] Reproduce issue on mobile viewport
- [ ] Identify root cause
- [ ] Apply minimal fix
- [ ] Run build/test/lint where available
- [ ] Capture before/after or describe manual verification
- [ ] Post final summary with files changed and residual risks

## Constraints

- Do not change backend APIs
- Do not modify auth/session logic
- Do not deploy without human approval

## Permission level

Autonomous:

- inspect repo;
- edit frontend files;
- run local checks;
- prepare commit/diff.

Needs human approval:

- deploy;
- merge PR;
- change environment variables;
- alter database schema.

## Completion report format

- Summary
- Files changed
- Commands run + exit codes
- Verification evidence
- Risks / follow-up
```

## Why this works

The same card can be read by:

- a product owner;
- an engineer;
- Hermes Kanban;
- GPT/Grok/Composer/Codex-style workers;
- a reviewer who returns later.

It avoids hidden context in chat and makes the task executable without making it opaque.
