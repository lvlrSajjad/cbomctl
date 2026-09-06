#!/usr/bin/env python3
"""Generate paste-ready syndicated copies from the canonical article.

Written rather than hand-converted so a correction to the canonical copy can
never leave a stale version on another platform. `--check` fails if a
syndicated copy has drifted, and CI runs it.

dev.to differences handled here:
  * frontmatter it understands, with canonical_url pointing home
  * MkDocs `!!! info` admonitions -> blockquotes
  * the `<!-- cbomctl: ... -->` generation markers stripped
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://lvlrsajjad.github.io/cbomctl"

ARTICLES = [
    {
        "src": ROOT / "docs" / "writing" / "rsa-2048-and-rsa-3072.md",
        "out": ROOT / "outreach" / "devto" / "rsa-2048-and-rsa-3072.md",
        "slug": "writing/rsa-2048-and-rsa-3072",
        "title": "RSA-2048 and RSA-3072 have different futures",
        "tags": "security, cryptography, postquantum, compliance",
    },
]


def admonition_to_quote(text: str) -> str:
    """`!!! info "Title"` + indented body -> a blockquote."""
    out, lines = [], text.split("\n")
    i = 0
    while i < len(lines):
        m = re.match(r'^!!! \w+(?: "(.*)")?\s*$', lines[i])
        if not m:
            out.append(lines[i]); i += 1; continue
        title = m.group(1)
        i += 1
        body = []
        while i < len(lines) and (lines[i].startswith("    ") or not lines[i].strip()):
            if lines[i].strip():
                body.append(lines[i][4:].rstrip())
            elif body:
                body.append("")
            i += 1
        while body and not body[-1]:
            body.pop()
        if title:
            out.append(f"> **{title}**")
            out.append(">")
        out += [f"> {b}" if b else ">" for b in body]
        out.append("")
    return "\n".join(out)


def render(article: dict) -> str:
    raw = article["src"].read_text()
    body = re.sub(r"^---\n.*?\n---\n", "", raw, count=1, flags=re.S)
    body = re.sub(r"<!-- cbomctl:.*?-->\n", "", body)          # generation markers
    # dev.to renders the title from frontmatter; a leading H1 duplicates it.
    body = re.sub(r"\A\s*# .*\n", "", body, count=1)
    body = admonition_to_quote(body).strip()

    canonical = f"{SITE}/{article['slug']}/"
    front = (
        "---\n"
        f"title: {article['title']}\n"
        "published: false\n"
        f"canonical_url: {canonical}\n"
        f"tags: {article['tags']}\n"
        "---\n\n"
    )
    footer = (
        f"\n\n---\n\n*Originally published at [{canonical}]({canonical}), which "
        "is the copy that gets corrected — this article describes a draft "
        "standard whose dates may move.*\n"
    )
    return front + body + footer


def main() -> int:
    check = "--check" in sys.argv
    stale = []
    for a in ARTICLES:
        content = render(a)
        if check:
            if not a["out"].is_file() or a["out"].read_text() != content:
                stale.append(a["out"].name)
        else:
            a["out"].parent.mkdir(parents=True, exist_ok=True)
            a["out"].write_text(content)
    if stale:
        print("stale syndicated copies (run scripts/gen_syndication.py):",
              ", ".join(stale))
        return 1
    print(f"{'checked' if check else 'wrote'} {len(ARTICLES)} syndicated copy(ies)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
