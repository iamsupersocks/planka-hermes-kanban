"""Shared mapping core for the Planka/Hermes stdio MCP server.

This module is the single bridge between MCP tool calls and the existing
``planka-build`` CLI (``planka_build.py`` from the hermes-kanban-lanes pack).
It deliberately contains NO Planka, Hermes, lane, worktree, or publication
rules — every semantic decision (lane tables, judge graphs, list names,
credential gates, SSH/psql transport) stays in the CLI, which remains the
canonical contract. The MCP layer only does:

- shape-level input validation (types, token patterns, length caps),
- injection-resistant argv construction (``--flag=value`` single tokens,
  argv lists, never a shell),
- a read/mutation gate (mutations disabled unless explicitly opted in),
- structured error propagation (validation, CLI resolution, exit codes,
  timeouts).

Because unknown lanes, sources, or reasoning efforts are rejected by the CLI
itself, this layer never enumerates them — it only checks that the value is a
safe token and lets the CLI's argparse own the semantics.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

SCHEMA_VERSION = "planka_hermes_mcp.v1"
SERVER_NAME = "planka-hermes"
SERVER_VERSION = "1.0.0"

# Path resolution override (documented in README.md next to this file).
# This is the only environment variable this layer reads; the behavioral
# settings (allow_mutations, timeout) are explicit server process arguments
# (--allow-mutations / --timeout-seconds) forwarded here, never env vars.
ENV_CLI = "PLANKA_BUILD_CLI"

DEFAULT_TIMEOUT_SECONDS = 300.0
_STDERR_TAIL_CHARS = 4000
_STDOUT_TAIL_CHARS = 200_000

# Shape-only patterns. Semantic validity (does the card exist, is the lane
# known) is the CLI's job.
_CARD_ID_RE = re.compile(r"^\d{1,20}$")
_TASK_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,63}$")
_TOKEN_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/:-]{0,63}$")

_TEXT_MAX = 20_000
_TITLE_MAX = 500
_PATH_MAX = 1_000


class ToolError(Exception):
    """Structured tool failure surfaced to the MCP client.

    ``code`` is a stable machine-readable identifier:
      invalid_input | unknown_tool | mutation_disabled | cli_not_found |
      cli_error | timeout
    """

    def __init__(self, code: str, message: str, details: Optional[dict] = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}

    def to_payload(self) -> dict:
        return {
            "schema": SCHEMA_VERSION,
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
            },
        }


# ─── Tool declarations ───────────────────────────────────────────────────────
#
# Each parameter spec: (json_type, required, validator_kind)
# validator kinds: card_id | task_id | token | text | title | path | bool

_TOOLS: List[Dict[str, Any]] = [
    {
        "name": "planka_hermes_doctor",
        "subcommand": "doctor",
        "read_only": True,
        "description": (
            "Run the planka-build doctor health report (Planka container, "
            "bridge, router, lane profiles, blocked-task diagnostics). "
            "Read-only. Returns the doctor JSON; a failing doctor surfaces "
            "as a structured cli_error with the report in details."
        ),
        "params": {},
    },
    {
        "name": "planka_hermes_show",
        "subcommand": "show",
        "read_only": True,
        "description": (
            "Show a Planka card (project, board, list, title, description) "
            "and its linked Hermes parent task. Read-only."
        ),
        "params": {
            "card_id": ("string", True, "card_id"),
        },
    },
    {
        "name": "planka_hermes_open",
        "subcommand": "open",
        "read_only": False,
        "description": (
            "Open (or find, idempotently) a CODE gate card on a Planka "
            "project and sync the Planka→Hermes bridge. Mutation: creates a "
            "card and comment when none exists."
        ),
        "params": {
            "project": ("string", True, "title"),
            "title": ("string", True, "title"),
            "repo": ("string", True, "path"),
            "acceptance": ("string", True, "text"),
        },
    },
    {
        "name": "planka_hermes_worker",
        "subcommand": "worker",
        "read_only": False,
        "description": (
            "Create the Hermes Kanban worker task (and judge task when the "
            "lane policy requires a judge graph) for a Planka card. Lane, "
            "source, and reasoning-effort semantics are validated by the "
            "planka-build CLI, which owns the lane contract. Mutation."
        ),
        "params": {
            "card_id": ("string", True, "card_id"),
            "parent_task": ("string", True, "task_id"),
            "repo": ("string", True, "path"),
            "title": ("string", True, "title"),
            "body": ("string", True, "text"),
            "lane": ("string", False, "token"),
            "fallback_reason": ("string", False, "text"),
            "source": ("string", False, "token"),
            "request": ("string", False, "text"),
            "model": ("string", False, "token"),
            "provider": ("string", False, "token"),
            "reasoning_effort": ("string", False, "token"),
        },
    },
    {
        "name": "planka_hermes_comment",
        "subcommand": "comment",
        "read_only": False,
        "description": "Add a comment to a Planka card. Mutation.",
        "params": {
            "card_id": ("string", True, "card_id"),
            "text": ("string", True, "text"),
        },
    },
    {
        "name": "planka_hermes_finish",
        "subcommand": "finish",
        "read_only": False,
        "description": (
            "Record QA evidence on a Planka card, complete the linked "
            "Hermes task, and move the card to Done (or Human Review). "
            "Mutation."
        ),
        "params": {
            "card_id": ("string", True, "card_id"),
            "evidence": ("string", True, "text"),
            "parent_task": ("string", False, "task_id"),
            "human_review": ("boolean", False, "bool"),
        },
    },
]

TOOLS_BY_NAME: Dict[str, Dict[str, Any]] = {t["name"]: t for t in _TOOLS}


def list_tools() -> List[Dict[str, Any]]:
    """Return MCP tool descriptors (name, description, inputSchema, annotations)."""
    out = []
    for tool in _TOOLS:
        properties = {}
        required = []
        for pname, (jtype, preq, _kind) in tool["params"].items():
            properties[pname] = {"type": jtype}
            if preq:
                required.append(pname)
        schema: Dict[str, Any] = {
            "type": "object",
            "properties": properties,
            "additionalProperties": False,
        }
        if required:
            schema["required"] = required
        out.append(
            {
                "name": tool["name"],
                "description": tool["description"],
                "inputSchema": schema,
                "annotations": {
                    "readOnlyHint": tool["read_only"],
                    "destructiveHint": not tool["read_only"],
                    "openWorldHint": True,
                },
            }
        )
    return out


# ─── Validation ──────────────────────────────────────────────────────────────


def _validate_value(tool: str, name: str, kind: str, value: Any) -> Any:
    def fail(reason: str) -> ToolError:
        return ToolError(
            "invalid_input",
            f"{tool}: parameter {name!r} {reason}",
            {"parameter": name},
        )

    if kind == "bool":
        if not isinstance(value, bool):
            raise fail("must be a boolean")
        return value
    if not isinstance(value, str):
        raise fail("must be a string")
    if kind == "card_id":
        if not _CARD_ID_RE.match(value):
            raise fail("must be a numeric Planka card id")
    elif kind == "task_id":
        if not _TASK_ID_RE.match(value):
            raise fail("must be a Hermes task id (alphanumeric/._:- token)")
    elif kind == "token":
        if not _TOKEN_RE.match(value):
            raise fail("must be a short identifier token")
    elif kind == "title":
        if not value.strip():
            raise fail("must be non-empty")
        if len(value) > _TITLE_MAX:
            raise fail(f"exceeds {_TITLE_MAX} characters")
    elif kind == "text":
        if not value.strip():
            raise fail("must be non-empty")
        if len(value) > _TEXT_MAX:
            raise fail(f"exceeds {_TEXT_MAX} characters")
    elif kind == "path":
        if not value.strip():
            raise fail("must be non-empty")
        if len(value) > _PATH_MAX:
            raise fail(f"exceeds {_PATH_MAX} characters")
        if value.lstrip().startswith("-"):
            raise fail("must not start with '-'")
    else:  # pragma: no cover - registry bug, not user input
        raise fail(f"has unknown validator kind {kind!r}")
    return value


def validate_arguments(tool_name: str, arguments: Optional[dict]) -> Dict[str, Any]:
    """Validate raw MCP arguments against the tool's parameter spec."""
    tool = TOOLS_BY_NAME.get(tool_name)
    if tool is None:
        raise ToolError("unknown_tool", f"unknown tool: {tool_name}")
    args = arguments or {}
    if not isinstance(args, dict):
        raise ToolError("invalid_input", f"{tool_name}: arguments must be an object")
    params = tool["params"]
    unexpected = sorted(set(args) - set(params))
    if unexpected:
        raise ToolError(
            "invalid_input",
            f"{tool_name}: unexpected parameter(s): {', '.join(unexpected)}",
            {"unexpected": unexpected},
        )
    cleaned: Dict[str, Any] = {}
    for pname, (_jtype, preq, kind) in params.items():
        if pname not in args or args[pname] is None:
            if preq:
                raise ToolError(
                    "invalid_input",
                    f"{tool_name}: missing required parameter {pname!r}",
                    {"parameter": pname},
                )
            continue
        cleaned[pname] = _validate_value(tool_name, pname, kind, args[pname])
    return cleaned


# ─── Argv construction ───────────────────────────────────────────────────────


def build_argv(tool_name: str, arguments: Optional[dict]) -> List[str]:
    """Map a validated tool call onto planka-build CLI argv (CLI prefix excluded).

    Every valued option is emitted as a single ``--flag=value`` token, so a
    value can never be reinterpreted as a separate flag by the CLI's argparse
    regardless of its content. Boolean options emit the bare constant flag
    only when true.
    """
    tool = TOOLS_BY_NAME.get(tool_name)
    if tool is None:
        raise ToolError("unknown_tool", f"unknown tool: {tool_name}")
    cleaned = validate_arguments(tool_name, arguments)
    argv: List[str] = [tool["subcommand"]]
    for pname, (_jtype, _preq, kind) in tool["params"].items():
        if pname not in cleaned:
            continue
        flag = "--" + pname.replace("_", "-")
        value = cleaned[pname]
        if kind == "bool":
            if value:
                argv.append(flag)
        else:
            argv.append(f"{flag}={value}")
    return argv


# ─── CLI resolution + execution ──────────────────────────────────────────────


def resolve_cli(env: Optional[dict] = None, cli_path: Optional[str] = None) -> List[str]:
    """Resolve the planka-build CLI into an argv prefix.

    Order: explicit ``cli_path`` (server ``--planka-build-cli``) → an
    executable or .py script → ``$PLANKA_BUILD_CLI`` → ``planka-build`` on
    PATH → ``~/.local/bin/planka-build``.
    """
    override = (cli_path or "").strip()
    if not override:
        e = os.environ if env is None else env
        override = (e.get(ENV_CLI) or "").strip()
    if override:
        path = Path(override).expanduser()
        if not path.is_file():
            raise ToolError(
                "cli_not_found",
                f"planka-build CLI path points to a missing file: {path}",
                {"path": str(path)},
            )
        if path.suffix == ".py":
            return [sys.executable, str(path)]
        return [str(path)]
    found = shutil.which("planka-build")
    if found:
        return [found]
    fallback = Path.home() / ".local" / "bin" / "planka-build"
    if fallback.is_file():
        return [str(fallback)]
    raise ToolError(
        "cli_not_found",
        "planka-build CLI not found: pass --planka-build-cli, set "
        "PLANKA_BUILD_CLI, or install planka-build on PATH",
    )


def run_tool(
    tool_name: str,
    arguments: Optional[dict],
    *,
    env: Optional[dict] = None,
    allow_mutations: bool = False,
    timeout_seconds: Optional[float] = None,
    cli_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Validate, gate, execute, and wrap one tool call.

    ``allow_mutations``, ``timeout_seconds`` and ``cli_path`` are explicit
    configuration forwarded by the server process from its ``--allow-mutations``,
    ``--timeout-seconds`` and ``--planka-build-cli`` arguments (falling back to
    defaults / ``$PLANKA_BUILD_CLI`` for the path). ``env`` is only used to
    pass through the process environment to the child CLI and to resolve the
    CLI path when ``cli_path`` is not given.

    Returns a success payload dict; raises :class:`ToolError` on any failure.
    """
    e = dict(os.environ if env is None else env)
    tool = TOOLS_BY_NAME.get(tool_name)
    if tool is None:
        raise ToolError("unknown_tool", f"unknown tool: {tool_name}")
    argv_suffix = build_argv(tool_name, arguments)
    if not tool["read_only"] and not allow_mutations:
        raise ToolError(
            "mutation_disabled",
            f"{tool_name} mutates Planka/Hermes state; start the MCP server "
            "with --allow-mutations to enable mutations",
            {"read_only_default": True},
        )
    cli = resolve_cli(e, cli_path=cli_path)
    timeout = (
        timeout_seconds
        if timeout_seconds is not None and timeout_seconds > 0
        else DEFAULT_TIMEOUT_SECONDS
    )
    try:
        proc = subprocess.run(
            cli + argv_suffix,
            env=e,
            text=True,
            capture_output=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        raise ToolError(
            "timeout",
            f"{tool_name}: planka-build did not finish within {timeout:g}s",
            {"timeout_seconds": timeout, "argv": argv_suffix},
        ) from None
    except OSError as exc:
        raise ToolError(
            "cli_error",
            f"{tool_name}: failed to execute planka-build: {exc}",
            {"argv": argv_suffix},
        ) from None

    stdout = proc.stdout or ""
    stdout_json: Any = None
    try:
        stdout_json = json.loads(stdout) if stdout.strip() else None
    except (ValueError, TypeError):
        stdout_json = None

    if proc.returncode != 0:
        details: Dict[str, Any] = {
            "exit_code": proc.returncode,
            "argv": argv_suffix,
            "stderr": (proc.stderr or "")[-_STDERR_TAIL_CHARS:],
        }
        if stdout_json is not None:
            details["stdout_json"] = stdout_json
        elif stdout:
            details["stdout"] = stdout[-_STDERR_TAIL_CHARS:]
        raise ToolError(
            "cli_error",
            f"{tool_name}: planka-build exited with code {proc.returncode}",
            details,
        )

    payload: Dict[str, Any] = {
        "schema": SCHEMA_VERSION,
        "tool": tool_name,
        "read_only": tool["read_only"],
        "exit_code": 0,
    }
    if stdout_json is not None:
        payload["result"] = stdout_json
    else:
        payload["result_text"] = stdout[-_STDOUT_TAIL_CHARS:]
    return payload
