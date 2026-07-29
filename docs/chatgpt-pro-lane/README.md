# ChatGPT Pro review lane

This folder documents an optional **read-only ChatGPT Pro review lane** for a Planka + Hermes Kanban workflow.

It is intentionally not a native Planka trigger and not a replacement for an implementation worker.

```text
Planka card
  human-visible objective, scope, constraints, evidence
      ↓
Hermes parent
  resolves the card, freezes an immutable source snapshot, runs deterministic checks
      ↓
Codex / worker lane
  optionally collects evidence or implements scoped changes in an isolated worktree
      ↓
ChatGPT Pro lane
  reviews a bounded, secret-free bundle through a verified ChatGPT browser session
      ↓
Hermes verification
  checks every useful finding against source, tests, logs, and the immutable revision
      ↓
Planka evidence
  records model proof, artifact links, accepted/rejected findings, blockers, and next decision
```

## What this lane is for

Use it for work where a second, high-effort reasoning pass is valuable:

- architecture review;
- release-readiness challenge;
- product and UX critique;
- long-document synthesis;
- risk and missing-test discovery;
- adversarial review of an implementation plan;
- bounded audit of an immutable commit.

Do not use it as evidence that code works, that a build shipped, or that a finding is true. ChatGPT Pro produces review hypotheses. Hermes owns verification.

## Important naming boundary

`ChatGPT Pro` is a ChatGPT product/model mode selected in the ChatGPT interface. It is not interchangeable with a Codex reasoning setting.

```text
ChatGPT Pro mode  ≠  Codex max
ChatGPT Pro mode  ≠  Codex ultra
ChatGPT Pro mode  ≠  a worker self-reporting that it used Pro
```

A valid Pro run must fail closed unless the browser automation verifies the exact requested model and the Pro control before submission. Never silently substitute another Codex model or effort tier.

## Files in this folder

- [`01-hermes-and-codex.md`](01-hermes-and-codex.md) — responsibilities, prerequisites, and invocation contract.
- [`02-planka-workflow.md`](02-planka-workflow.md) — card lifecycle, comments, artifacts, and state transitions.
- [`03-security-and-verification.md`](03-security-and-verification.md) — secret boundary, immutable evidence, verification, and failure handling.
- [`card-template.md`](card-template.md) — copy/paste Planka card and evidence-comment templates.

## Default operating rule

The Pro lane is **manual or orchestrator-selected by default**.

A label such as `review:chatgpt-pro` may express human intent, but moving a card or adding a label should not directly launch a browser with privileged credentials. Hermes must first validate scope, data sensitivity, bundle size, source revision, and required approvals.

## Completion rule

A Pro response alone never moves a card to `Done`.

The card may move to review only after Hermes has:

1. verified the requested model and Pro mode;
2. saved the output as an artifact;
3. checked important findings against the real source;
4. rerun required deterministic verification;
5. recorded accepted, rejected, and unresolved findings in Planka.
