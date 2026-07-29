# Planka card template — ChatGPT Pro review

Use this template for a bounded review request. The card requests a review; it does not directly launch a privileged browser.

```markdown
## Objective
Use the read-only ChatGPT Pro lane to challenge `<plan / architecture / release candidate / product decision>`.

## Why Pro is useful here
Explain why a high-effort second review is worth the time and cost.

## Source of truth
- Repository or artifact:
- Branch:
- Immutable SHA/version:
- Worktree clean: yes/no
- Existing Planka/Hermes task:

## Scope
Pro may analyze:
- ...

Pro must not:
- modify files;
- access GitHub, Planka, production, or credentials;
- claim that commands were run;
- expand beyond the attached evidence.

## Evidence bundle
Allowlisted files:
- `00-evidence-brief.md`
- `...`

Explicit exclusions:
- `.env` and secrets;
- browser/session data;
- dependency/build directories;
- private customer/member data;
- unrelated binary artifacts.

## Questions for the reviewer
1. ...
2. ...
3. ...

## Requested output
For every finding:
- severity;
- evidence file and excerpt;
- why it matters;
- deterministic verification Hermes should run;
- recommended next action;
- fact vs hypothesis.

## Acceptance criteria
- [ ] Exact requested model verified by the browser runner.
- [ ] Pro mode verified before submission.
- [ ] Output saved as an artifact.
- [ ] Important findings checked against the real source by Hermes.
- [ ] Required deterministic checks rerun by Hermes.
- [ ] Accepted, rejected, and unresolved findings recorded separately.
- [ ] No implementation, push, merge, deploy, or publishing performed by the review lane.

## Human approval required before
- implementation outside the existing scope;
- merge or deploy;
- public publication of review artifacts;
- credential or permission changes;
- destructive action.
```

## Blocked comment

```markdown
ChatGPT Pro review blocked.

Reason: `<model/mode proof missing | browser auth expired | unsafe bundle | source revision ambiguous | missing evidence>`
What was verified: `<facts>`
What was not executed: no fallback model, no implementation, no external side effect.
Needed next: `<human input or repair>`
```

## Verification handoff

```markdown
Hermes verification of ChatGPT Pro review

Source reviewed: `<repo>` @ `<sha>`
Pro evidence: requested=`<model>`, resolved=`<model>`, Pro verified=`yes/no`

Accepted findings:
- `<finding>` — verified by `<file/command>`

Rejected findings:
- `<finding>` — contradicted by `<source context>`

Unresolved:
- `<finding>` — requires `<human decision/missing environment>`

Artifacts:
- Pro review: `<path or safe URL>`
- Verification table: `<path or safe URL>`

Next state: `<Review Required | Blocked | Done for review-only objective>`
```
