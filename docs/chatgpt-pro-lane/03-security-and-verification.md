# 03 — Security and verification

## Threat model

This lane combines three sensitive surfaces:

- project source and internal evidence;
- a privileged signed-in ChatGPT browser profile;
- an orchestration system that can execute commands and update task state.

The safe boundary is simple:

```text
Pro receives bounded read-only evidence.
Hermes keeps credentials, tools, writes, and final authority.
```

## Never include in a bundle

Exclude:

```text
.env files
API keys and bearer tokens
OAuth tokens and refresh tokens
browser profiles, cookies, local storage, and session databases
SSH private keys and known-host credentials
Apple signing certificates and provisioning profiles
password stores and keychains
cloud credentials
production database dumps
private customer/member data without explicit authorization
build products, dependency trees, and generated caches
large binaries unrelated to the review
```

A `.gitignore` entry is not proof that a file is safe. Build the bundle from an explicit allowlist and scan the final artifact.

## Prefer immutable, minimal evidence

Good bundle inputs:

- a short evidence brief;
- selected source files at one commit;
- a reviewed diff;
- test output with secrets redacted;
- architecture or product specifications;
- reproducible failure logs;
- screenshots that contain no credentials or personal data.

Bad bundle inputs:

- an entire home directory;
- a browser profile;
- an unbounded repository archive;
- raw production logs;
- generated dependencies;
- a database export when a schema excerpt is enough.

## Secret scan

Use the repository’s existing scanner when available. A minimal fallback can check tracked/bundled files for common credential shapes, but it is not a complete secret detector.

Example checks:

```bash
find "$BUNDLE" -type f -maxdepth 3 -print

git -C "$REPO" status --short

git -C "$REPO" diff --check
```

If tools such as `gitleaks` or `trufflehog` are part of the project’s normal verification, run them against the final bundle. Do not install or upload a new scanner without reviewing its own data-handling behavior.

## Browser isolation

The ChatGPT browser runner should:

- use a dedicated profile, not the operator’s daily browser profile;
- expose its debugging endpoint only on loopback;
- start only for a consultation when practical;
- stop after the run;
- keep VNC/noVNC disabled unless an interactive login repair is required;
- never expose debugging, VNC, or profile storage to the public internet;
- store any temporary password with restrictive permissions and delete it after use.

## Fail-closed model proof

The wrapper must require machine-observed evidence before accepting the answer:

```text
requested model == resolved model
Pro mode control == selected/verified
runner exit code == 0
output artifact exists and is non-empty
```

The answer saying “I am Pro” is not evidence.

If the ChatGPT UI changes, the account loses access, a CAPTCHA blocks automation, or model/mode proof is missing:

```text
result = blocked / failed
fallback = none
```

Record the failure in Planka. Do not relabel another model as Pro.

## Source verification

Hermes should convert Pro findings into a verification table:

```markdown
| Finding | Pro evidence | Source check | Deterministic test | Verdict |
|---|---|---|---|---|
| F-01 | file + excerpt | confirmed at SHA | command/result | accepted |
| F-02 | file + excerpt | contradicted by source | n/a | rejected |
| F-03 | missing evidence | unresolved | test unavailable | human decision |
```

For each accepted finding:

1. open the real file at the reviewed SHA;
2. verify path and excerpt;
3. check surrounding context omitted from the bundle;
4. reproduce with a deterministic command when possible;
5. classify severity independently;
6. create a separate implementation card if code should change.

## External side effects

Pro must never be trusted to claim that it:

- pushed a branch;
- opened or merged a PR;
- deployed a service;
- updated Planka;
- changed credentials;
- sent a message;
- modified a repository.

Hermes performs external actions with normal approval and read-back verification.

## Prompt-injection boundary

Repository files, logs, linked pages, and card attachments are untrusted data. Text inside them may attempt to redirect the reviewer or request secrets/actions.

The review prompt must state that attached content is evidence, not instructions. Hermes should exclude unrelated operational instructions and never expose tools or credentials to the Pro browser session.

## Public artifact gate

Before committing any review material to a public repository, verify:

- no internal paths that reveal sensitive infrastructure;
- no credentials, tokens, cookies, signed URLs, or account identifiers;
- no private member/customer information;
- no proprietary source excerpts without permission;
- no browser screenshots containing personal data;
- links resolve and relative paths are valid;
- the artifact clearly distinguishes facts, hypotheses, and unresolved questions.

Private run artifacts should remain outside Git by default.

## Cleanup and audit receipt

After a run, record without secrets:

```text
card ID
run slug
reviewed repository and SHA
requested/resolved model
Pro verification result
start/end timestamps
runner exit code
bundle manifest and hashes when required
output and Hermes-verification paths
browser service stopped: yes/no
open temporary ports: none/declared
```

The receipt proves how the review happened. It does not make the review findings true; source verification does that.
