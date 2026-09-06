#!/usr/bin/env python3
"""Generate paste-ready syndicated copies from the canonical article.

Written rather than hand-converted so a correction to the canonical copy can
never leave a stale version on another platform. `--check` fails if a
syndicated copy has drifted, and CI runs it.

dev.to's current editor has SEPARATE fields for title, tags and canonical URL
(the last under "Advanced Post options"), and the body box takes plain markdown
with no frontmatter. Pasting a frontmatter block there renders it as literal
text. So this emits two files:

  <slug>.body.md    exactly what goes in the Post Content box
  <slug>.fields.md  what to type into the surrounding fields

Handled in the body: MkDocs `!!! info` admonitions become blockquotes, the
`<!-- cbomctl: ... -->` generation markers are stripped, and the duplicate H1
is removed because the title field supplies it.
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
        "out": ROOT / "outreach" / "devto" / "rsa-2048-and-rsa-3072.body.md",
        "fields": ROOT / "outreach" / "devto" / "rsa-2048-and-rsa-3072.fields.md",
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
    footer = (
        f"\n\n---\n\n*Originally published at [{canonical}]({canonical}), which "
        "is the copy that gets corrected — this article describes a draft "
        "standard whose dates may move.*\n"
    )
    return body + footer


def render_fields(article: dict) -> str:
    canonical = f"{SITE}/{article['slug']}/"
    tags = [t.strip() for t in article["tags"].split(",")]
    assert len(tags) <= 4, "dev.to allows at most 4 tags"
    return (
        f"# dev.to fields — {article['title']}\n\n"
        "The editor has separate fields for these. Do **not** paste them into\n"
        "the body; there is no frontmatter in the current dev.to editor.\n\n"
        "## Post Title\n\n"
        f"```\n{article['title']}\n```\n\n"
        "## Tags (max 4)\n\n"
        f"```\n{' '.join(tags)}\n```\n\n"
        "## Canonical URL\n\n"
        "**Advanced Post options** (button below the editor) -> the field with\n"
        "placeholder `https://yoursite.com/post-title`:\n\n"
        f"```\n{canonical}\n```\n\n"
        "This is the one that matters. Without it dev.to outranks your own site\n"
        "for your own writing, and readers land on the copy you will forget to\n"
        "correct — which for an article about a *draft* standard is the whole\n"
        "problem.\n\n"
        "## Body\n\n"
        f"`{article['out'].name}` — paste the whole file into **Post Content**.\n"
    )


def main() -> int:
    check = "--check" in sys.argv
    stale = []
    for a in ARTICLES:
        for path, content in ((a["out"], render(a)), (a["fields"], render_fields(a))):
            if check:
                if not path.is_file() or path.read_text() != content:
                    stale.append(path.name)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content)
    if stale:
        print("stale syndicated copies (run scripts/gen_syndication.py):",
              ", ".join(stale))
        return 1
    print(f"{'checked' if check else 'wrote'} {len(ARTICLES)} syndicated copy(ies)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
