# 02 — Planka operating workflow

## No direct trigger by default

Planka remains the human cockpit. It expresses intent and stores evidence; it should not directly own a privileged ChatGPT browser session.

A label such as:

```text
review:chatgpt-pro
```

means “Hermes should consider the Pro review lane.” It does not mean “launch Pro immediately.”

Hermes must run a preflight first.

## Preflight gate

Before invoking Pro, verify:

- card objective is specific;
- acceptance criteria exist;
- source repository/path is known;
- immutable commit or explicit dirty patch is recorded;
- included files are allowlisted;
- secrets and generated artifacts are excluded;
- bundle size is bounded;
- requested output is review/analysis, not an unapproved side effect;
- required deterministic tests have run or are explicitly missing;
- a human decision boundary is stated for merge, deploy, publishing, deletion, or credentials.

If the gate fails, comment the missing fields and move the card to `Blocked` rather than improvising.

## Suggested lifecycle

```text
Ready for Agent
  card requests or permits a Pro review
      ↓
In Progress
  Hermes freezes evidence and runs the private Pro consultation
      ↓
Review Required / Human Review
  Pro artifact exists and Hermes verification is attached
      ↓
Done
  accepted actions are verified, or the review-only objective is complete
```

Failure path:

```text
model/mode not verified
browser login expired
CAPTCHA or UI changed
bundle unsafe or too large
source revision ambiguous
required evidence missing
      ↓
Blocked
```

Never silently fall back to Codex `max`, `ultra`, or another model while preserving the label “Pro.”

## Start comment

When the lane starts, add a concise comment:

```markdown
ChatGPT Pro review started.

Mode: read-only challenger
Source: `<repo>` @ `<sha>`
Bundle: `<private artifact path or artifact ID>`
Deterministic checks before review:
- `<command>` → `<result>`

Boundaries:
- no repository writes;
- no Planka writes by Pro;
- no push, merge, deploy, publishing, or credential changes;
- Hermes will verify every accepted finding.
```

Do not paste cookies, auth state, signed URLs, private browser paths, or full sensitive command output into Planka.

## Final evidence comment

After Hermes verifies the result:

```markdown
ChatGPT Pro review completed and independently checked by Hermes.

Model evidence:
- requested model: `<model>`
- resolved model: `<model>`
- Pro mode verified: yes
- runner exit: `0`

Artifacts:
- Pro review: `<path or safe URL>`
- Hermes verification: `<path or safe URL>`
- source revision: `<sha>`

Findings:
- accepted: `<count>`
- rejected after source check: `<count>`
- unresolved / human decision: `<count>`

Deterministic verification:
- `<command>` → `<result>`

Next decision:
- `<implementation card, approval, or no further action>`
```

If the runner cannot prove the requested model and Pro mode, record the run as failed. Do not attach its answer as a valid Pro review.

## Relationship with implementation cards

A review card and an implementation card should usually be separate.

```text
Review card
  asks Pro to challenge evidence and identify risks
      ↓
Hermes verifies findings
      ↓
Implementation card(s)
  contain accepted changes, scope, tests, and permission boundary
```

This prevents a reviewer from quietly expanding scope or turning suggestions into unapproved code changes.

Each implementation card should link back to:

- the review card;
- immutable source SHA reviewed;
- exact accepted finding;
- required tests;
- rejected alternatives when relevant.

## Re-review after changes

Do not reuse a verdict against a different commit.

After implementation:

1. record the new SHA;
2. rerun deterministic checks;
3. build a delta-only bundle when possible;
4. ask Pro to review the delta only if the risk justifies it;
5. verify again with Hermes;
6. update Planka with the new immutable evidence.

A review is valid only for the revision it names.

## Manual lane versus automation

Start manually. Automate only after the manual loop is stable and auditable.

A future bridge may detect `review:chatgpt-pro`, but it should create a **pending review request**, not launch the browser immediately. Hermes still owns:

- data classification;
- source freeze;
- bundle construction;
- secret scan;
- invocation approval;
- output verification;
- Planka reconciliation.
