# 01 — Using ChatGPT Pro from Hermes and Codex

## Role separation

The safest design keeps orchestration, execution, review, and truth separate.

```text
Hermes parent       = lifecycle owner, bundle owner, final verifier
Codex/worker        = scoped execution and deterministic evidence collection
ChatGPT Pro         = read-only challenger/reviewer
Planka              = human-visible operational state and evidence
Git                 = immutable source revision and code history
```

ChatGPT Pro must not own Git, Planka, deployment, or task completion.

## Prerequisites

A private runner needs:

- a dedicated browser profile already signed in to ChatGPT;
- browser automation able to select the requested model and Pro mode;
- a wrapper that fails closed when model or mode verification is absent;
- a bounded file attachment mechanism;
- a private output directory outside the repository;
- deterministic checks that Hermes can rerun independently.

The public repository must not contain the browser profile, cookies, session storage, access tokens, pairing codes, certificates, or screenshots containing credentials.

## Wrapper contract

The examples below assume a local command exposed through:

```bash
export ORACLE_PRO_CMD="$HOME/.hermes-opus/scripts/oracle_pro.py"
```

That path is an implementation example, not a repository requirement. Another private browser runner is acceptable if it enforces the same contract.

The runner should support:

```text
prompt input
one or more bounded file attachments
unique run/session slug
output file path
timeout
non-zero exit when exact model or Pro mode is not verified
browser cleanup after completion
```

Example invocation:

```bash
set -euo pipefail

CARD_ID="1234567890"
RUN_ROOT="$HOME/.local/state/planka-pro-runs/$CARD_ID"
BUNDLE="$RUN_ROOT/bundle"
mkdir -p "$BUNDLE"

"$ORACLE_PRO_CMD" \
  --slug "planka-$CARD_ID-review-01" \
  --file "$BUNDLE/00-evidence-brief.md" \
  --file "$BUNDLE/10-source-excerpts.md" \
  --file "$BUNDLE/20-test-results.txt" \
  --output "$RUN_ROOT/pro-review.md" \
  "$(cat "$RUN_ROOT/prompt.md")" \
  | tee "$RUN_ROOT/oracle-run.log"
```

Do not pass secrets on the command line. Process arguments may be visible to other local users and may be retained in logs.

## Preparing an immutable bundle

Hermes should resolve and record the exact source before asking Pro to review it.

```bash
REPO="/path/to/repository"
SHA="$(git -C "$REPO" rev-parse HEAD)"
BRANCH="$(git -C "$REPO" branch --show-current)"
git -C "$REPO" status --short
printf 'branch=%s\nsha=%s\n' "$BRANCH" "$SHA"
```

Prefer a clean worktree at an immutable commit. If the relevant state is dirty, either create a patch artifact deliberately or stop and ask which state should be reviewed. Never describe an uncommitted checkout as a reproducible release candidate.

A useful evidence brief records:

- Planka card ID and objective;
- repository and immutable SHA;
- branch/worktree state;
- exact files included and omitted;
- deterministic commands already run;
- known limitations;
- questions Pro should challenge;
- actions Pro must not perform.

## Using Codex before Pro

Codex may prepare a bounded lane in an isolated worktree:

- inspect the repository;
- run tests and static checks;
- collect relevant excerpts;
- draft an implementation plan;
- produce a diff for review.

Codex output is not automatically trusted. Hermes reviews the diff and reruns required checks before including evidence in the Pro bundle.

Recommended order:

```text
Planka contract
→ isolated Codex/worktree lane when needed
→ Hermes diff and test review
→ immutable bundle
→ ChatGPT Pro challenge
→ Hermes source verification
```

## Prompt contract

The Pro prompt should state:

- the exact objective;
- the immutable revision;
- the evidence hierarchy;
- the allowed analysis scope;
- known missing evidence;
- requested output format;
- a prohibition on claiming external actions or repository access;
- a requirement to cite attached filenames and excerpts for findings.

Example:

```text
You are a read-only reviewer. Review only the attached evidence for Planka card <CARD_ID> at commit <SHA>.

Do not claim that you opened the live repository, ran commands, changed files, pushed code, or updated Planka. You have no such access.

For every finding return:
- severity;
- evidence file and quoted excerpt;
- why it matters;
- deterministic verification Hermes should run;
- recommended next action.

Separate demonstrated facts from hypotheses. Mark missing evidence explicitly.
```

## Output contract

Store at least:

```text
prompt.md
bundle/00-evidence-brief.md
bundle/...
oracle-run.log
pro-review.md
hermes-verification.md
```

Keep the run directory private unless every artifact passes the public-repository safety checks in [`03-security-and-verification.md`](03-security-and-verification.md).
