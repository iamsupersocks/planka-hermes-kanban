#!/usr/bin/env python3
"""Thin stdio MCP server for the Planka/Hermes build loop.

Exposes the planka-build CLI (the canonical Planka/Hermes contract) as MCP
tools over newline-delimited JSON-RPC 2.0 on stdio, so Codex, Cursor, Hermes,
and any generic MCP client share exactly the same behavior as the CLI.

Stdlib only — no MCP SDK dependency — so any Python 3.10+ can launch it:

    python3 mcp/planka-hermes/server.py

All tool semantics live in planka_hermes_mcp_core.py (validation, argv
mapping, mutation gate, structured errors); this file only speaks the wire
protocol: initialize, ping, tools/list, tools/call.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Optional

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import planka_hermes_mcp_core as core  # noqa: E402

PROTOCOL_VERSION = "2025-06-18"
_SUPPORTED_PROTOCOL_VERSIONS = frozenset({PROTOCOL_VERSION})

_JSONRPC_PARSE_ERROR = -32700
_JSONRPC_INVALID_REQUEST = -32600
_JSONRPC_METHOD_NOT_FOUND = -32601
_JSONRPC_INVALID_PARAMS = -32602


class ServerConfig:
    """Explicit server-process configuration, carried through to core.run_tool.

    Populated from the process arguments (--allow-mutations,
    --timeout-seconds, --planka-build-cli) so every MCP client configures the
    server identically via args, never via bespoke environment variables.
    """

    def __init__(
        self,
        *,
        allow_mutations: bool = False,
        timeout_seconds: float = core.DEFAULT_TIMEOUT_SECONDS,
        cli_path: Optional[str] = None,
    ) -> None:
        self.allow_mutations = allow_mutations
        self.timeout_seconds = timeout_seconds
        self.cli_path = cli_path


def _write(stream, obj: dict) -> None:
    stream.write(json.dumps(obj, ensure_ascii=False) + "\n")
    stream.flush()


def _response(req_id: Any, result: dict) -> dict:
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def _error(req_id: Any, code: int, message: str) -> dict:
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}


def _tool_error_result(err: core.ToolError) -> dict:
    payload = err.to_payload()
    return {
        "content": [{"type": "text", "text": json.dumps(payload, ensure_ascii=False)}],
        "structuredContent": payload,
        "isError": True,
    }


def _handle_initialize(params: dict) -> dict:
    # MCP protocol negotiation: answer with the version we support. If the
    # client asks for exactly the version we speak, echo it back; otherwise
    # (different or absent version) respond with our supported version rather
    # than blindly echoing an arbitrary client value.
    client_version = params.get("protocolVersion")
    if isinstance(client_version, str) and client_version in _SUPPORTED_PROTOCOL_VERSIONS:
        version = client_version
    else:
        version = PROTOCOL_VERSION
    return {
        "protocolVersion": version,
        "capabilities": {"tools": {"listChanged": False}},
        "serverInfo": {"name": core.SERVER_NAME, "version": core.SERVER_VERSION},
    }


def _handle_tools_call(params: dict, config: ServerConfig) -> dict:
    name = params.get("name")
    arguments = params.get("arguments") or {}
    if not isinstance(name, str) or not name:
        raise core.ToolError("invalid_input", "tools/call requires a tool 'name'")
    if not isinstance(arguments, dict):
        raise core.ToolError("invalid_input", f"{name}: 'arguments' must be an object")
    payload = core.run_tool(
        name,
        arguments,
        allow_mutations=config.allow_mutations,
        timeout_seconds=config.timeout_seconds,
        cli_path=config.cli_path,
    )
    return {
        "content": [{"type": "text", "text": json.dumps(payload, ensure_ascii=False)}],
        "structuredContent": payload,
        "isError": False,
    }


def handle_message(message: dict, config: Optional[ServerConfig] = None) -> Optional[dict]:
    """Handle one decoded JSON-RPC message; return the response (None for notifications)."""
    cfg = config if config is not None else ServerConfig()
    req_id = message.get("id")
    method = message.get("method")
    params = message.get("params") or {}
    is_notification = "id" not in message

    if not isinstance(method, str):
        # A response from the client (or garbage) — nothing to answer.
        if is_notification:
            return None
        return _error(req_id, _JSONRPC_INVALID_REQUEST, "missing method")
    if not isinstance(params, dict):
        if is_notification:
            return None
        return _error(req_id, _JSONRPC_INVALID_PARAMS, "params must be an object")

    if method.startswith("notifications/"):
        return None
    if method == "initialize":
        return _response(req_id, _handle_initialize(params))
    if method == "ping":
        return _response(req_id, {})
    if method == "tools/list":
        return _response(req_id, {"tools": core.list_tools()})
    if method == "tools/call":
        try:
            return _response(req_id, _handle_tools_call(params, cfg))
        except core.ToolError as err:
            # Tool failures are results with isError, not protocol errors.
            return _response(req_id, _tool_error_result(err))
    if is_notification:
        return None
    return _error(req_id, _JSONRPC_METHOD_NOT_FOUND, f"method not found: {method}")


def serve(
    stdin=None,
    stdout=None,
    config: Optional[ServerConfig] = None,
) -> None:
    stream_in = stdin if stdin is not None else sys.stdin
    stream_out = stdout if stdout is not None else sys.stdout
    cfg = config if config is not None else ServerConfig()
    for line in stream_in:
        line = line.strip()
        if not line:
            continue
        try:
            message = json.loads(line)
        except (ValueError, TypeError):
            _write(stream_out, _error(None, _JSONRPC_PARSE_ERROR, "parse error"))
            continue
        if not isinstance(message, dict):
            _write(stream_out, _error(None, _JSONRPC_INVALID_REQUEST, "request must be an object"))
            continue
        reply = handle_message(message, cfg)
        if reply is not None:
            _write(stream_out, reply)


def main(argv: Optional[list] = None) -> None:
    """Parse process arguments and serve over stdio."""
    import argparse

    parser = argparse.ArgumentParser(
        prog="planka-hermes-mcp",
        description="Path-driven stdio MCP server for the planka-build CLI.",
    )
    parser.add_argument(
        "--allow-mutations",
        action="store_true",
        help="Enable the mutating tools (open/worker/comment/finish). Off by default.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=core.DEFAULT_TIMEOUT_SECONDS,
        help="Per-call planka-build timeout in seconds (default: %(default)g).",
    )
    parser.add_argument(
        "--planka-build-cli",
        default=None,
        help="Path to the planka-build executable or planka_build.py script "
        "(default: $PLANKA_BUILD_CLI, then planka-build on PATH, then "
        "~/.local/bin/planka-build).",
    )
    args = parser.parse_args(argv)
    config = ServerConfig(
        allow_mutations=args.allow_mutations,
        timeout_seconds=args.timeout_seconds,
        cli_path=args.planka_build_cli,
    )
    serve(config=config)


if __name__ == "__main__":
    main()
