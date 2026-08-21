"""Unit tests for the Planka/Hermes stdio MCP server (mcp/planka-hermes).

Covers: input validation, tool→CLI argv mapping, read/mutation gating,
structured error propagation (exit codes, timeouts, missing CLI), command
injection resistance, and the JSON-RPC message handler. Uses only stdlib +
pytest; the "CLI" is always a fake temp script — no Planka, Hermes, SSH, or
network access.
"""
from __future__ import annotations

import importlib.util
import io
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

_SERVER_DIR = Path(__file__).resolve().parents[1] / "mcp" / "planka-hermes"


def _load(module_name: str, filename: str):
    spec = importlib.util.spec_from_file_location(module_name, _SERVER_DIR / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


core = _load("planka_hermes_mcp_core", "planka_hermes_mcp_core.py")
server = _load("planka_hermes_mcp_server", "server.py")

ALL_TOOLS = {
    "planka_hermes_doctor",
    "planka_hermes_show",
    "planka_hermes_open",
    "planka_hermes_worker",
    "planka_hermes_comment",
    "planka_hermes_finish",
}


@pytest.fixture
def fake_cli(tmp_path):
    """A fake planka-build that echoes its argv as JSON and exits 0."""
    path = tmp_path / "fake_planka_build.py"
    path.write_text(
        "#!/usr/bin/env python3\n"
        "import json, sys\n"
        'sys.stdout.write(json.dumps({"argv": sys.argv[1:]}))\n',
        encoding="utf-8",
    )
    return path


def _env(cli_path, **extra):
    env = {"PATH": "", core.ENV_CLI: str(cli_path)}
    env.update(extra)
    return env


# ─── Tool listing ────────────────────────────────────────────────────────────


class TestListTools:
    def test_exposes_the_six_planka_tools(self):
        names = {t["name"] for t in core.list_tools()}
        assert ALL_TOOLS <= names

    def test_read_mutation_annotations_are_consistent(self):
        for tool in core.list_tools():
            read_only = core.TOOLS_BY_NAME[tool["name"]]["read_only"]
            assert tool["annotations"]["readOnlyHint"] is read_only
            assert tool["annotations"]["destructiveHint"] is not read_only

    def test_schemas_declare_required_and_reject_extras(self):
        by_name = {t["name"]: t for t in core.list_tools()}
        show = by_name["planka_hermes_show"]["inputSchema"]
        assert show["required"] == ["card_id"]
        assert show["additionalProperties"] is False
        doctor = by_name["planka_hermes_doctor"]["inputSchema"]
        assert "required" not in doctor


# ─── Validation ──────────────────────────────────────────────────────────────


class TestValidation:
    def test_unknown_tool(self):
        with pytest.raises(core.ToolError) as exc:
            core.validate_arguments("planka_hermes_nope", {})
        assert exc.value.code == "unknown_tool"

    def test_missing_required(self):
        with pytest.raises(core.ToolError) as exc:
            core.validate_arguments("planka_hermes_show", {})
        assert exc.value.code == "invalid_input"
        assert exc.value.details["parameter"] == "card_id"

    def test_unexpected_parameter_rejected(self):
        with pytest.raises(core.ToolError) as exc:
            core.validate_arguments(
                "planka_hermes_show", {"card_id": "1", "evil": "x"}
            )
        assert exc.value.code == "invalid_input"
        assert exc.value.details["unexpected"] == ["evil"]

    def test_wrong_type_rejected(self):
        with pytest.raises(core.ToolError):
            core.validate_arguments("planka_hermes_show", {"card_id": 123})
        with pytest.raises(core.ToolError):
            core.validate_arguments(
                "planka_hermes_finish",
                {"card_id": "1", "evidence": "e", "human_review": "yes"},
            )

    @pytest.mark.parametrize(
        "card_id",
        ["", "abc", "12 34", "123; rm -rf /", "$(reboot)", "-1", "1" * 21],
    )
    def test_hostile_or_malformed_card_ids_rejected(self, card_id):
        with pytest.raises(core.ToolError) as exc:
            core.validate_arguments("planka_hermes_show", {"card_id": card_id})
        assert exc.value.code == "invalid_input"

    def test_task_id_token_shapes(self):
        ok = core.validate_arguments(
            "planka_hermes_finish",
            {"card_id": "1", "evidence": "e", "parent_task": "t_78c1556d"},
        )
        assert ok["parent_task"] == "t_78c1556d"
        with pytest.raises(core.ToolError):
            core.validate_arguments(
                "planka_hermes_finish",
                {"card_id": "1", "evidence": "e", "parent_task": "-rf"},
            )

    def test_empty_and_oversized_text_rejected(self):
        with pytest.raises(core.ToolError):
            core.validate_arguments(
                "planka_hermes_comment", {"card_id": "1", "text": "   "}
            )
        with pytest.raises(core.ToolError):
            core.validate_arguments(
                "planka_hermes_comment", {"card_id": "1", "text": "x" * 20_001}
            )

    def test_lane_shape_only_semantics_left_to_cli(self):
        # The MCP layer must NOT duplicate the lane table: any safe token
        # passes shape validation; the CLI rejects unknown lanes itself.
        args = {
            "card_id": "1", "parent_task": "t_1", "repo": "/tmp/r",
            "title": "t", "body": "b", "lane": "some-future-lane",
        }
        assert core.validate_arguments("planka_hermes_worker", args)["lane"] == (
            "some-future-lane"
        )
        with pytest.raises(core.ToolError):
            core.validate_arguments(
                "planka_hermes_worker", {**args, "lane": "--lane injection"}
            )


# ─── Argv mapping / injection resistance ─────────────────────────────────────


class TestArgvMapping:
    def test_doctor(self):
        assert core.build_argv("planka_hermes_doctor", {}) == ["doctor"]

    def test_show(self):
        assert core.build_argv("planka_hermes_show", {"card_id": "42"}) == [
            "show", "--card-id=42",
        ]

    def test_open(self):
        argv = core.build_argv(
            "planka_hermes_open",
            {"project": "Codex Ops", "title": "MCP lot 1",
             "repo": "/home/x/repo", "acceptance": "tests green"},
        )
        assert argv == [
            "open", "--project=Codex Ops", "--title=MCP lot 1",
            "--repo=/home/x/repo", "--acceptance=tests green",
        ]

    def test_worker_full(self):
        argv = core.build_argv(
            "planka_hermes_worker",
            {"card_id": "7", "parent_task": "t_a", "repo": "/r", "title": "T",
             "body": "B", "lane": "composer", "fallback_reason": "why",
             "source": "codex", "model": "composer-2.5-fast",
             "provider": "openrouter", "reasoning_effort": "low"},
        )
        assert argv == [
            "worker", "--card-id=7", "--parent-task=t_a", "--repo=/r",
            "--title=T", "--body=B", "--lane=composer",
            "--fallback-reason=why", "--source=codex",
            "--model=composer-2.5-fast", "--provider=openrouter",
            "--reasoning-effort=low",
        ]

    def test_finish_boolean_flag(self):
        with_review = core.build_argv(
            "planka_hermes_finish",
            {"card_id": "1", "evidence": "ok", "human_review": True},
        )
        assert with_review == [
            "finish", "--card-id=1", "--evidence=ok", "--human-review",
        ]
        without = core.build_argv(
            "planka_hermes_finish",
            {"card_id": "1", "evidence": "ok", "human_review": False},
        )
        assert without == ["finish", "--card-id=1", "--evidence=ok"]

    def test_flag_lookalike_text_stays_one_token(self):
        """A body crafted to look like extra CLI flags cannot become separate
        argv entries: valued options are single --flag=value tokens."""
        argv = core.build_argv(
            "planka_hermes_comment",
            {"card_id": "1", "text": "--human-review --evidence=fake"},
        )
        assert argv == [
            "comment", "--card-id=1", "--text=--human-review --evidence=fake",
        ]
        assert all("\n" not in a or a.startswith("--text=") for a in argv)


# ─── Execution: gating, propagation, timeouts ────────────────────────────────


class TestRunTool:
    def test_read_only_tool_runs_without_gate(self, fake_cli):
        payload = core.run_tool("planka_hermes_doctor", {}, env=_env(fake_cli))
        assert payload["exit_code"] == 0
        assert payload["read_only"] is True
        assert payload["result"] == {"argv": ["doctor"]}

    def test_mutation_blocked_by_default(self, fake_cli):
        with pytest.raises(core.ToolError) as exc:
            core.run_tool(
                "planka_hermes_comment",
                {"card_id": "1", "text": "hi"},
                env=_env(fake_cli),
            )
        assert exc.value.code == "mutation_disabled"

    def test_mutation_allowed_with_opt_in(self, fake_cli):
        payload = core.run_tool(
            "planka_hermes_comment",
            {"card_id": "1", "text": "hi"},
            env=_env(fake_cli),
            allow_mutations=True,
        )
        assert payload["result"] == {"argv": ["comment", "--card-id=1", "--text=hi"]}

    def test_validation_happens_before_gate_and_subprocess(self, tmp_path):
        # Missing CLI + hostile input: invalid_input wins — nothing executes.
        with pytest.raises(core.ToolError) as exc:
            core.run_tool(
                "planka_hermes_show",
                {"card_id": "1; reboot"},
                env={"PATH": "", core.ENV_CLI: str(tmp_path / "missing")},
            )
        assert exc.value.code == "invalid_input"

    def test_cli_not_found(self, tmp_path):
        with pytest.raises(core.ToolError) as exc:
            core.run_tool(
                "planka_hermes_doctor", {},
                env={"PATH": "", core.ENV_CLI: str(tmp_path / "missing.py")},
            )
        assert exc.value.code == "cli_not_found"

    def test_nonzero_exit_propagates_structured_error(self, tmp_path):
        cli = tmp_path / "failing.py"
        cli.write_text(
            "#!/usr/bin/env python3\n"
            "import json, sys\n"
            'sys.stdout.write(json.dumps({"ok": False, "why": "doctor red"}))\n'
            'sys.stderr.write("gate refused")\n'
            "sys.exit(2)\n",
            encoding="utf-8",
        )
        with pytest.raises(core.ToolError) as exc:
            core.run_tool("planka_hermes_doctor", {}, env=_env(cli))
        err = exc.value
        assert err.code == "cli_error"
        assert err.details["exit_code"] == 2
        assert "gate refused" in err.details["stderr"]
        assert err.details["stdout_json"] == {"ok": False, "why": "doctor red"}

    def test_timeout_maps_to_structured_error(self, fake_cli, monkeypatch):
        # Do not launch a real sleeping process (it collides with the
        # tests/conftest.py subprocess isolation/guard). Simulate the timeout
        # by having subprocess.run raise TimeoutExpired, then assert the
        # structured timeout error.
        def _raise_timeout(*args, **kwargs):
            raise subprocess.TimeoutExpired(
                cmd=["python", str(fake_cli), "doctor"], timeout=0.5
            )

        monkeypatch.setattr(core.subprocess, "run", _raise_timeout)
        with pytest.raises(core.ToolError) as exc:
            core.run_tool(
                "planka_hermes_doctor",
                {},
                env=_env(fake_cli),
                timeout_seconds=0.5,
            )
        assert exc.value.code == "timeout"
        assert exc.value.details["timeout_seconds"] == 0.5
        assert exc.value.details["argv"] == ["doctor"]

    def test_non_json_stdout_returned_as_text(self, tmp_path):
        cli = tmp_path / "plain.py"
        cli.write_text(
            "#!/usr/bin/env python3\nprint('not json')\n", encoding="utf-8"
        )
        payload = core.run_tool("planka_hermes_doctor", {}, env=_env(cli))
        assert payload["result_text"].strip() == "not json"


class TestResolveCli:
    def test_py_override_uses_interpreter(self, fake_cli):
        argv = core.resolve_cli({core.ENV_CLI: str(fake_cli)})
        assert argv == [sys.executable, str(fake_cli)]

    def test_executable_override_used_directly(self, tmp_path):
        exe = tmp_path / "planka-build"
        exe.write_text("#!/bin/sh\n", encoding="utf-8")
        argv = core.resolve_cli({core.ENV_CLI: str(exe)})
        assert argv == [str(exe)]

    def test_missing_override_is_structured(self, tmp_path):
        with pytest.raises(core.ToolError) as exc:
            core.resolve_cli({core.ENV_CLI: str(tmp_path / "nope")})
        assert exc.value.code == "cli_not_found"

    def test_explicit_cli_path_wins_over_env(self, fake_cli, tmp_path):
        # --planka-build-cli (explicit arg) must take precedence over the env.
        other = tmp_path / "other.py"
        other.write_text("#!/usr/bin/env python3\n", encoding="utf-8")
        argv = core.resolve_cli(
            {core.ENV_CLI: str(other)}, cli_path=str(fake_cli)
        )
        assert argv == [sys.executable, str(fake_cli)]


# ─── JSON-RPC message handler ────────────────────────────────────────────────


class TestHandleMessage:
    def test_initialize(self):
        reply = server.handle_message(
            {"jsonrpc": "2.0", "id": 1, "method": "initialize",
             "params": {"protocolVersion": "2025-06-18"}}
        )
        assert reply["result"]["serverInfo"]["name"] == "planka-hermes"
        assert reply["result"]["protocolVersion"] == "2025-06-18"
        assert "tools" in reply["result"]["capabilities"]

    def test_initialize_negotiates_supported_client_version(self):
        # A client requesting exactly the version we speak gets it echoed back.
        reply = server.handle_message(
            {"jsonrpc": "2.0", "id": 1, "method": "initialize",
             "params": {"protocolVersion": "2025-06-18"}}
        )
        assert reply["result"]["protocolVersion"] == "2025-06-18"

    def test_initialize_negotiates_unsupported_client_version_down(self):
        # A client asking for a DIFFERENT version must NOT get it echoed back:
        # per MCP negotiation the server answers with the version it supports.
        reply = server.handle_message(
            {"jsonrpc": "2.0", "id": 1, "method": "initialize",
             "params": {"protocolVersion": "2024-11-05"}}
        )
        assert reply["result"]["protocolVersion"] == "2025-06-18"
        assert reply["result"]["protocolVersion"] != "2024-11-05"

    def test_initialize_without_client_version_defaults_to_supported(self):
        reply = server.handle_message(
            {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
        )
        assert reply["result"]["protocolVersion"] == "2025-06-18"

    def test_tools_list(self):
        reply = server.handle_message(
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}
        )
        names = {t["name"] for t in reply["result"]["tools"]}
        assert ALL_TOOLS <= names

    def test_notifications_get_no_reply(self):
        assert server.handle_message(
            {"jsonrpc": "2.0", "method": "notifications/initialized"}
        ) is None

    def test_unknown_method_is_jsonrpc_error(self):
        reply = server.handle_message(
            {"jsonrpc": "2.0", "id": 3, "method": "resources/list"}
        )
        assert reply["error"]["code"] == -32601

    def test_tool_error_is_result_with_iserror(self, monkeypatch):
        reply = server.handle_message(
            {"jsonrpc": "2.0", "id": 4, "method": "tools/call",
             "params": {"name": "planka_hermes_show",
                        "arguments": {"card_id": "not-a-card"}}}
        )
        result = reply["result"]
        assert result["isError"] is True
        assert result["structuredContent"]["error"]["code"] == "invalid_input"
        assert "error" not in reply  # tool failure ≠ protocol failure

    def test_tools_call_success_via_fake_cli(self, fake_cli, monkeypatch):
        monkeypatch.setenv(core.ENV_CLI, str(fake_cli))
        reply = server.handle_message(
            {"jsonrpc": "2.0", "id": 5, "method": "tools/call",
             "params": {"name": "planka_hermes_show",
                        "arguments": {"card_id": "99"}}}
        )
        result = reply["result"]
        assert result["isError"] is False
        assert result["structuredContent"]["result"] == {
            "argv": ["show", "--card-id=99"]
        }
        # content mirrors structuredContent as JSON text
        assert json.loads(result["content"][0]["text"]) == result["structuredContent"]


# ─── serve(): injected streams + explicit config ─────────────────────────────


class TestServe:
    def test_serve_respects_injected_streams(self):
        # Answers must go to the injected stdout, not sys.stdout, so a caller
        # can capture the protocol in-process (this is what a test harness /
        # embedding uses).
        stdin = io.StringIO(
            '{"jsonrpc":"2.0","id":1,"method":"initialize",'
            '"params":{"protocolVersion":"2025-06-18"}}\n'
            '{"jsonrpc":"2.0","id":2,"method":"ping"}\n'
        )
        stdout = io.StringIO()
        server.serve(stdin=stdin, stdout=stdout)
        replies = [json.loads(line) for line in stdout.getvalue().splitlines() if line]
        assert [r["id"] for r in replies] == [1, 2]
        assert replies[0]["result"]["protocolVersion"] == "2025-06-18"
        assert replies[1]["result"] == {}

    def test_serve_passes_explicit_config_to_run_tool(self, fake_cli):
        # The server forwards --allow-mutations / --planka-build-cli into
        # core.run_tool: a mutation succeeds only when config allows it.
        cfg = server.ServerConfig(allow_mutations=True, cli_path=str(fake_cli))
        stdin = io.StringIO(
            '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":'
            '{"name":"planka_hermes_comment","arguments":'
            '{"card_id":"1","text":"hi"}}}\n'
        )
        stdout = io.StringIO()
        server.serve(stdin=stdin, stdout=stdout, config=cfg)
        reply = json.loads(stdout.getvalue().splitlines()[0])
        assert reply["result"]["isError"] is False
        assert reply["result"]["structuredContent"]["result"]["argv"] == [
            "comment", "--card-id=1", "--text=hi",
        ]

    def test_serve_mutation_blocked_without_config(self):
        # Without --allow-mutations the explicit config keeps mutations off.
        stdin = io.StringIO(
            '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":'
            '{"name":"planka_hermes_comment","arguments":'
            '{"card_id":"1","text":"hi"}}}\n'
        )
        stdout = io.StringIO()
        server.serve(stdin=stdin, stdout=stdout)
        reply = json.loads(stdout.getvalue().splitlines()[0])
        assert reply["result"]["isError"] is True
        assert reply["result"]["structuredContent"]["error"]["code"] == (
            "mutation_disabled"
        )


# ─── End-to-end smoke (real subprocess over stdio) ───────────────────────────


class TestSmoke:
    def test_smoke_script_passes(self):
        proc = subprocess.run(
            [sys.executable, str(_SERVER_DIR / "smoke.py")],
            text=True,
            capture_output=True,
            timeout=120,
        )
        assert proc.returncode == 0, proc.stdout + proc.stderr
        assert "SMOKE PASS" in proc.stdout


# ─── Public HEAD contract (docs honesty + leak scan) ─────────────────────────


_REPO_ROOT = Path(__file__).resolve().parents[1]
_MCP_README = _REPO_ROOT / "mcp" / "planka-hermes" / "README.md"

# Generic content guards — deliberately NOT encoded with any real ID / host.
# Matching is by shape so no live identifier has to appear in the repository.
_ANYWORD_NUM16_20 = re.compile(r"(?<![0-9])[0-9]{16,20}(?![0-9])")
_HOME_USER = re.compile(r"/home/([A-Za-z0-9_][A-Za-z0-9._-]*)")
# Placeholder usernames tolerated in docs and test fixtures.
_PLACEHOLDER_USERS = {"you", "x"}
# Internal DNS suffixes, assembled from codepoints so they don't leak verbatim.
_HOME_ARPA = "".join(chr(c) for c in (104, 111, 109, 101, 46, 97, 114, 112, 97))
_DOT_TS_NET = "." + "".join(chr(c) for c in (116, 115, 46, 110, 101, 116))


def _tracked_file_texts() -> dict[str, str]:
    proc = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=_REPO_ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    texts = {}
    for rel in proc.stdout.split("\0"):
        if not rel:
            continue
        path = _REPO_ROOT / rel
        if not path.is_file():
            continue
        try:
            texts[rel] = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            texts[rel] = path.read_bytes().decode("utf-8", errors="replace")
    return texts


class TestPublicHeadContract:
    def test_tracked_files_have_no_live_identifiers(self):
        hits = []
        for rel, text in _tracked_file_texts().items():
            # Refuse any autonomous 16–20 digit number (Planka/Telegram id shape).
            for tok in _ANYWORD_NUM16_20.findall(text):
                hits.append(f"{rel}: 16–20 digit token {tok!r}")

            # Refuse internal DNS suffixes that would leak a precise host.
            if _HOME_ARPA in text:
                hits.append(f"{rel}: {_HOME_ARPA} host suffix")
            if _DOT_TS_NET in text:
                hits.append(f"{rel}: {_DOT_TS_NET} host suffix")

            # Refuse absolute user-home paths that are not documented placeholders,
            # while tolerating /home/you, /home/x and temp fixture paths.
            for user in _HOME_USER.findall(text):
                if user not in _PLACEHOLDER_USERS:
                    hits.append(f"{rel}: non-placeholder absolute path /home/{user}")
        assert hits == [], "public HEAD still exposes live identifiers: " + "; ".join(hits)

    def test_readme_documents_env_inheritance_and_stdio_tails(self):
        text = _MCP_README.read_text(encoding="utf-8")
        required = (
            "run_tool",
            "os.environ",
            "result_text",
            "details.stderr",
            "details.stdout_json",
            "details.stdout",
            "--allow-mutations",
        )
        missing = [token for token in required if token not in text]
        assert missing == [], f"MCP README missing honesty tokens: {missing}"
        assert "disabled by default" in text or "Off by default" in text or "off (read-only)" in text
        # Example card_id must stay a placeholder, not a live Planka id.
        assert '"card_id":"1234567890"' in text
