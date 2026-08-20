# Planka/Hermes MCP Server

A thin stdio MCP server that exposes the existing `planka-build` CLI (the
Supersocks Planka/Hermes build loop from the `hermes-kanban-lanes` pack) to
any MCP client — Codex, Cursor, Hermes itself, or a generic stdio client —
so every surface uses **exactly the same contract** as the CLI.

The server duplicates **no** Planka, Hermes, lane, worktree, or publication
rules. Every tool call is validated for shape, then mapped onto a
`planka-build <subcommand> --flag=value` argv list (never a shell), and the
CLI remains the single source of truth for lane tables, judge graphs,
credential gates, list names, and SSH/psql transport.

Stdlib only (Python 3.10+). No MCP SDK, no pip install, no manifest — launch
it by path.

## Install from this repo

The server ships **inside this repository** and is launched by absolute path —
there is nothing to install. It needs only Python 3.10+ in your `python3` and a
`planka-build` CLI (the `planka_build.py` script from the `hermes-kanban-lanes`
pack) reachable via `--planka-build-cli`, `$PLANKA_BUILD_CLI`, or PATH.

Point every MCP client at:

```text
<checkout>/mcp/planka-hermes/server.py
```

where `<checkout>` is the root of this repo (e.g. `~/src/planka-hermes-kanban`).
The `--planka-build-cli` argument must point at your deployed `planka-build`
executable or `planka_build.py` script.

## Tools

| Tool | CLI subcommand | Kind |
|---|---|---|
| `planka_hermes_doctor` | `doctor` | read-only |
| `planka_hermes_show` | `show` | read-only |
| `planka_hermes_open` | `open` | mutation |
| `planka_hermes_worker` | `worker` | mutation |
| `planka_hermes_comment` | `comment` | mutation |
| `planka_hermes_finish` | `finish` | mutation |

Read-only tools carry `readOnlyHint: true` annotations. **Mutations are
disabled by default**: mutating tools return a structured `mutation_disabled`
error unless the server process is started with `--allow-mutations`.

## Server arguments

All behavioral settings are configured with explicit process arguments, so
every MCP client configures the server identically (no bespoke environment
variables for behavior):

| Argument | Meaning | Default |
|---|---|---|
| `--allow-mutations` | Enable the four mutating tools (open/worker/comment/finish) | off (read-only) |
| `--timeout-seconds N` | Per-call planka-build timeout in seconds | `300` |
| `--planka-build-cli PATH` | Path to the `planka-build` executable or `planka_build.py` script | `$PLANKA_BUILD_CLI`, then `planka-build` on PATH, then `~/.local/bin/planka-build` |

`--allow-mutations` and `--timeout-seconds` are always passed as *arguments*;
the only environment variable this server reads is `PLANKA_BUILD_CLI`, which
is purely a path-resolution override for the CLI:

| Variable | Meaning | Default |
|---|---|---|
| `PLANKA_BUILD_CLI` | Path to the `planka-build` executable or `planka_build.py` script | `planka-build` on PATH, then `~/.local/bin/planka-build` |

All other environment variables (`PLANKA_SSH_TARGET`, `HERMES_HOME`,
`HERMES_KANBAN_BOARD`, …) are passed through unchanged to the CLI, which owns
their semantics. No secrets are read, stored, or logged by this server.

## Structured errors

Failures come back as tool results with `isError: true` and a stable JSON
body:

```json
{"schema": "planka_hermes_mcp.v1",
 "error": {"code": "cli_error", "message": "...", "details": {"exit_code": 2, "stderr": "..."}}}
```

Codes: `invalid_input`, `unknown_tool`, `mutation_disabled`,
`cli_not_found`, `cli_error` (nonzero exit; includes the CLI's JSON output
in `details.stdout_json` when parseable — e.g. a failing `doctor` report),
`timeout`.

## Client configuration

Replace `/path/to/planka-hermes-kanban` and `/home/you/.local/bin/planka-build`
with your checkout root and deployed CLI. Every client below passes the same
explicit arguments (`--allow-mutations` when you want mutations,
`--timeout-seconds` to tune the CLI timeout), so behavior is identical across
Codex, Cursor, and Hermes.

### Codex (`~/.codex/config.toml`)

```toml
[mcp_servers.planka-hermes]
command = "python3"
args = [
  "/path/to/planka-hermes-kanban/mcp/planka-hermes/server.py",
  "--timeout-seconds", "300",
  "--planka-build-cli", "/home/you/.local/bin/planka-build",
  # Uncomment to allow open/worker/comment/finish:
  # "--allow-mutations",
]
```

### Cursor (`~/.cursor/mcp.json` or `.cursor/mcp.json`)

```json
{
  "mcpServers": {
    "planka-hermes": {
      "command": "python3",
      "args": [
        "/path/to/planka-hermes-kanban/mcp/planka-hermes/server.py",
        "--timeout-seconds", "300",
        "--planka-build-cli", "/home/you/.local/bin/planka-build"
      ]
    }
  }
}
```

### Hermes (`~/.hermes/config.yaml`)

```yaml
mcp_servers:
  planka-hermes:
    command: python3
    args:
      - /path/to/planka-hermes-kanban/mcp/planka-hermes/server.py
      - --timeout-seconds
      - "300"
      - --planka-build-cli
      - /home/you/.local/bin/planka-build
```

`PLANKA_BUILD_CLI` is honored as a path override if you prefer to keep the
CLI out of the args (e.g. because the path differs per developer), but the
args form above gives identical, self-contained configuration everywhere.

### Generic stdio client

The transport is newline-delimited JSON-RPC 2.0 on stdin/stdout:

```bash
printf '%s\n%s\n%s\n' \
  '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18"}}' \
  '{"jsonrpc":"2.0","id":2,"method":"tools/list"}' \
  '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"planka_hermes_show","arguments":{"card_id":"1846010765941671745"}}}' \
  | python3 mcp/planka-hermes/server.py
```

## Verification

Run from this repo's root. Local smoke (no Planka/Hermes/network access —
uses a fake CLI):

```bash
python3 mcp/planka-hermes/smoke.py
```

Unit tests (pytest, stdlib only; the "CLI" is always a fake temp script):

```bash
python3 -m pytest tests/test_planka_hermes_mcp.py -q
```
