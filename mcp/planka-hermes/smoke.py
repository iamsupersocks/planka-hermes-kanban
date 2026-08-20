#!/usr/bin/env python3
"""Local smoke test for the Planka/Hermes MCP server.

Spawns server.py as a real stdio subprocess wired to a FAKE planka-build CLI
(a temp script that echoes JSON), then walks the full client flow:

  initialize → tools/list → doctor (read-only, succeeds) →
  comment (mutation, blocked by default gate) →
  comment (mutation, allowed when launched with --allow-mutations) →
  injection probe (hostile card_id rejected before any subprocess runs)

No Planka, Hermes, SSH, or network access is touched. Exit 0 + "SMOKE PASS"
on success; nonzero with a diagnostic on the first failure.

Run:  python3 mcp/planka-hermes/smoke.py
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent

FAKE_CLI = """#!/usr/bin/env python3
import json, sys
sys.stdout.write(json.dumps({"fake_cli": True, "argv": sys.argv[1:]}))
"""


class SmokeClient:
    def __init__(self, env: dict, extra_args: list | None = None):
        cmd = [sys.executable, str(HERE / "server.py")]
        if extra_args:
            cmd.extend(extra_args)
        self.proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
            env=env,
        )
        self._next_id = 0

    def request(self, method: str, params: dict | None = None) -> dict:
        self._next_id += 1
        msg = {"jsonrpc": "2.0", "id": self._next_id, "method": method}
        if params is not None:
            msg["params"] = params
        assert self.proc.stdin and self.proc.stdout
        self.proc.stdin.write(json.dumps(msg) + "\n")
        self.proc.stdin.flush()
        line = self.proc.stdout.readline()
        if not line:
            raise RuntimeError(f"server closed stdout while awaiting {method}")
        reply = json.loads(line)
        if reply.get("id") != self._next_id:
            raise RuntimeError(f"id mismatch on {method}: {reply}")
        return reply

    def close(self) -> None:
        if self.proc.stdin:
            self.proc.stdin.close()
        self.proc.wait(timeout=10)


def check(label: str, condition: bool, context: object = "") -> None:
    if not condition:
        print(f"SMOKE FAIL: {label}\n  context: {context}")
        sys.exit(1)
    print(f"  ok: {label}")


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="planka-hermes-smoke-") as tmp:
        fake_cli = Path(tmp) / "fake_planka_build.py"
        fake_cli.write_text(FAKE_CLI, encoding="utf-8")

        env = dict(os.environ)
        env["PLANKA_BUILD_CLI"] = str(fake_cli)

        client = SmokeClient(env)
        try:
            init = client.request(
                "initialize",
                {"protocolVersion": "2025-06-18", "capabilities": {},
                 "clientInfo": {"name": "smoke", "version": "0"}},
            )
            check(
                "initialize returns serverInfo",
                init.get("result", {}).get("serverInfo", {}).get("name") == "planka-hermes",
                init,
            )

            listed = client.request("tools/list")
            tools = {t["name"]: t for t in listed.get("result", {}).get("tools", [])}
            expected = {
                "planka_hermes_doctor", "planka_hermes_show", "planka_hermes_open",
                "planka_hermes_worker", "planka_hermes_comment", "planka_hermes_finish",
            }
            check("tools/list exposes the 6 planka tools", expected <= set(tools), sorted(tools))
            check(
                "doctor is annotated read-only, finish is not",
                tools["planka_hermes_doctor"]["annotations"]["readOnlyHint"]
                and not tools["planka_hermes_finish"]["annotations"]["readOnlyHint"],
                {n: t["annotations"] for n, t in tools.items()},
            )

            doctor = client.request(
                "tools/call", {"name": "planka_hermes_doctor", "arguments": {}}
            )
            result = doctor.get("result", {})
            structured = result.get("structuredContent", {})
            check("doctor call succeeds against fake CLI", result.get("isError") is False, doctor)
            check(
                "doctor maps to the 'doctor' subcommand",
                structured.get("result", {}).get("argv") == ["doctor"],
                structured,
            )

            blocked = client.request(
                "tools/call",
                {"name": "planka_hermes_comment",
                 "arguments": {"card_id": "123", "text": "smoke"}},
            )
            b_result = blocked.get("result", {})
            check(
                "mutation blocked without --allow-mutations",
                b_result.get("isError") is True
                and b_result.get("structuredContent", {}).get("error", {}).get("code")
                == "mutation_disabled",
                blocked,
            )

            injected = client.request(
                "tools/call",
                {"name": "planka_hermes_show",
                 "arguments": {"card_id": "123; rm -rf /"}},
            )
            i_result = injected.get("result", {})
            check(
                "hostile card_id rejected as invalid_input",
                i_result.get("isError") is True
                and i_result.get("structuredContent", {}).get("error", {}).get("code")
                == "invalid_input",
                injected,
            )
        finally:
            client.close()

        env_mut = dict(env)
        client = SmokeClient(env_mut, extra_args=["--allow-mutations"])
        try:
            client.request("initialize", {"protocolVersion": "2025-06-18"})
            allowed = client.request(
                "tools/call",
                {"name": "planka_hermes_comment",
                 "arguments": {"card_id": "123", "text": "smoke ok"}},
            )
            a_result = allowed.get("result", {})
            a_argv = a_result.get("structuredContent", {}).get("result", {}).get("argv")
            check(
                "mutation allowed with --allow-mutations, argv uses --flag=value tokens",
                a_result.get("isError") is False
                and a_argv == ["comment", "--card-id=123", "--text=smoke ok"],
                allowed,
            )
        finally:
            client.close()

    print("SMOKE PASS")


if __name__ == "__main__":
    main()
