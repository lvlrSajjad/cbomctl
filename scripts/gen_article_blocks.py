#!/usr/bin/env python3
"""Regenerate every code block in prose that claims to be tool output.

Article 2 was drafted with a hand-written demo showing RSA-2048 and RSA-3072
getting different verdicts. They did not: the security_level selector was
inert, so the prose described behaviour the tool did not have. That is the
exact failure this project exists to catch in other people's compliance
claims, and prose is not exempt from it.

Mark a block in any Markdown file:

    <!-- cbomctl: verdict tests/fixtures/rsa-strength-split.json -j nist-ir8547 | head -16 -->
    ```
    ...replaced with real output...
    ```

`--check` fails if any block is stale, and CI runs it.

Only `cbomctl` subcommands run, invoked directly with no shell. A trailing
`| head -N` is honoured as a line limit, not as a real pipe.
"""

from __future__ import annotations

import re
import shlex
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKER = re.compile(
    r"(?P<marker><!--\s*cbomctl:\s*(?P<cmd>[^>]*?)\s*-->\n)"
    r"```(?P<lang>[a-z]*)\n(?P<body>.*?)```",
    re.S,
)
#: README.md is listed by name, not by walking ROOT: a bare ROOT.rglob would
#: sweep .research/, virtualenvs and every vendored tree. It is here because
#: it was the one file outside the checked tree, and its demo block drifted
#: into fiction unnoticed while every article stayed honest.
SEARCH = [ROOT / "README.md", ROOT / "articles", ROOT / "docs", ROOT / "outreach"]


def run(cmd: str) -> str:
    limit = None
    if "|" in cmd:
        cmd, _, tail = cmd.partition("|")
        parts = shlex.split(tail)
        if len(parts) == 2 and parts[0] == "head" and parts[1].lstrip("-").isdigit():
            limit = int(parts[1].lstrip("-"))
        else:
            raise SystemExit(f"only `| head -N` is supported, got: {tail!r}")

    args = shlex.split(cmd.strip())
    if args and args[0] == "cbomctl":
        args = args[1:]
    proc = subprocess.run(
        [sys.executable, "-m", "cbomctl.cli", *args],
        capture_output=True, text=True, cwd=ROOT,
        env={**dict(__import__("os").environ), "PYTHONPATH": str(ROOT / "src"),
             "NO_COLOR": "1", "TERM": "dumb", "COLUMNS": "100"},
    )
    if proc.returncode == 2:
        raise SystemExit(f"command failed (usage error): cbomctl {cmd}\n{proc.stderr}")
    lines = [ln.rstrip() for ln in proc.stdout.rstrip("\n").split("\n")]
    if limit is not None:
        lines = lines[:limit]
    return "\n".join(lines) + "\n"


def process(path: Path, check: bool) -> bool:
    original = path.read_text()

    def repl(m: re.Match) -> str:
        fresh = run(m.group("cmd"))
        return f"{m.group('marker')}```{m.group('lang')}\n{fresh}```"

    updated = MARKER.sub(repl, original)
    if updated == original:
        return True
    if check:
        print(f"stale: {path.relative_to(ROOT)}")
        return False
    path.write_text(updated)
    print(f"updated: {path.relative_to(ROOT)}")
    return True


def main() -> int:
    check = "--check" in sys.argv
    ok, seen = True, 0
    for base in SEARCH:
        paths = [base] if base.is_file() else sorted(base.rglob("*.md"))
        for path in paths:
            if MARKER.search(path.read_text()):
                seen += 1
                ok &= process(path, check)
    if not ok:
        print("\nRun scripts/gen_article_blocks.py to refresh. A block that "
              "drifts from real output is prose describing a tool that does "
              "not exist.")
        return 1
    print(f"{'checked' if check else 'refreshed'} {seen} file(s) with generated blocks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
