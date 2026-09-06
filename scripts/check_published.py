#!/usr/bin/env python3
"""Diff the articles that are actually live against the copies in this repo.

`gen_syndication.py --check` pins `outreach/devto/` to `docs/writing/`, so a
correction to the canonical article cannot leave a stale file on disk. It stops
at the edge of the repository. The copy that a reader sees is on dev.to, and
between the file and that copy sits a paste into a browser — where the first
attempt mangled 206 characters into Mac Roman, and where a later correction can
simply not be made.

dev.to publishes `body_markdown` through its public read API with no
authentication, so that last gap is closeable: fetch the published post, undo
the one transform its editor applies on save, and diff. Both articles were live
and byte-identical when this file was written, which is the answer to "is this
worth having" — it is cheap, and it is the only thing in the repository that
can tell you a published correction did not land.

    python3 scripts/check_published.py

**Not fatal by default.** A drifted published post is a real finding, and this
exits non-zero for it. But an unreachable dev.to, a deleted post or an article
not yet published are reported and *not* failures: they are states a reader has
to see, not reasons to redden an unrelated commit. `--strict` makes every
non-PASS fatal, which is the mode to run before publishing more articles.

**LinkedIn is not checkable and is not pretended to be.** LinkedIn's API
requires an authenticated app review for `r_member_social`, and post text is
not served to anonymous clients. There is no read path for
`outreach/linkedin/*.txt`, so `outreach/syndication.md` says so at the point
where someone is about to paste. That is the honest half of this file.
"""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

_spec = importlib.util.spec_from_file_location(
    "gen_syndication", ROOT / "scripts" / "gen_syndication.py")
gen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gen)

API = "https://dev.to/api/articles"


def fetch(url: str) -> dict | None:
    """A dev.to API document, or None if dev.to could not be reached."""
    try:
        with urllib.request.urlopen(url, timeout=20) as fh:
            return json.load(fh)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return {}
        return None
    except Exception:
        # A python.org build with no CA bundle cannot verify dev.to, and that
        # is a fact about this laptop, not about the article. `pypi_has` in
        # check_commands.py makes the same distinction for the same reason.
        proc = subprocess.run(
            ["curl", "-sS", "--max-time", "25", "-w", "\n%{http_code}", url],
            capture_output=True, text=True)
        body, _, code = proc.stdout.rpartition("\n")
        if code.strip() == "404":
            return {}
        if code.strip() != "200":
            return None
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return None


def api_path(url: str) -> str | None:
    """`https://dev.to/<user>/<slug>` -> the read-API path for that post."""
    m = re.match(r"https://dev\.to/([\w-]+)/([\w-]+)/?$", url)
    return f"{API}/{m.group(1)}/{m.group(2)}" if m else None


def as_published(body: str) -> str:
    """The local body, as dev.to stores it after a save.

    Exactly one transform, applied because it is the one dev.to's editor makes
    and not because it makes a diff go away: a bare *opening* fence is saved as
    ```plaintext, and the closing fence is left bare. Anything else that
    differs is drift, and shows up as drift.
    """
    out, inside = [], False
    for line in body.split("\n"):
        if line.startswith("```"):
            if not inside and line.rstrip() == "```":
                line = "```plaintext"
            inside = not inside
        out.append(line)
    return "\n".join(out)


def diff(local: str, published: str) -> list[str]:
    import difflib
    a = as_published(local).rstrip("\n").split("\n")
    b = published.replace("\r\n", "\n").rstrip("\n").split("\n")
    return [ln for ln in difflib.unified_diff(
        a, b, "local (outreach/devto/)", "published (dev.to)", lineterm="", n=1)]


def check(article: dict, report: list) -> str:
    """PASS / FAIL / SKIP / UNPUBLISHED for one article."""
    name = article["out"].name
    url = article.get("devto")
    if not url:
        report.append(("UNPUBLISHED", name, (
            "no dev.to URL recorded. If it is live, add it to ARTICLES in "
            "scripts/gen_syndication.py so it is checked from now on")))
        return "UNPUBLISHED"

    path = api_path(url)
    if path is None:
        report.append(("FAIL", name, f"`{url}` is not a dev.to article URL"))
        return "FAIL"

    doc = fetch(path)
    if doc is None:
        report.append(("SKIP", name, "dev.to unreachable — not verified"))
        return "SKIP"
    if doc == {}:
        report.append(("FAIL", name, (
            f"dev.to returns 404 for {url} — the post was deleted, unpublished "
            f"or renamed. Its canonical URL points at our site, so a reader "
            f"following an old link now lands nowhere")))
        return "FAIL"

    ok = True
    canonical = f"{gen.SITE}/{article['slug']}/"
    if doc.get("canonical_url") != canonical:
        report.append(("FAIL", name, (
            f"canonical_url is {doc.get('canonical_url')!r}, expected "
            f"{canonical!r} — without it dev.to outranks the copy that gets "
            f"corrected")))
        ok = False
    if doc.get("title") != article["title"]:
        report.append(("FAIL", name, (
            f"published title is {doc.get('title')!r}, "
            f"the fields file says {article['title']!r}")))
        ok = False
    want_tags = [t.strip() for t in article["tags"].split(",")]
    # The list endpoint returns `tag_list` as a list; the single-article
    # endpoint returns it as a comma-joined string and puts the list in `tags`.
    raw_tags = doc.get("tags") if isinstance(doc.get("tags"), list) \
        else doc.get("tag_list")
    got_tags = sorted(raw_tags) if isinstance(raw_tags, list) \
        else sorted(t.strip() for t in (raw_tags or "").split(",") if t.strip())
    if got_tags != sorted(want_tags):
        report.append(("FAIL", name, (
            f"published tags {got_tags} != {sorted(want_tags)}")))
        ok = False

    lines = diff(article["out"].read_text(), doc.get("body_markdown") or "")
    if lines:
        shown = "\n        ".join(lines[:24])
        report.append(("FAIL", name, (
            f"the published body has drifted from {article['out'].name}:\n"
            f"        {shown}"
            + ("\n        ..." if len(lines) > 24 else ""))))
        ok = False

    if ok:
        report.append(("PASS", name, (
            f"published copy is byte-identical, canonical URL and tags correct "
            f"— {url}")))
    return "PASS" if ok else "FAIL"


def main() -> int:
    strict = "--strict" in sys.argv
    report: list[tuple[str, str, str]] = []
    verdicts = [check(a, report) for a in gen.ARTICLES]

    width = max((len(w) for _, w, _ in report), default=0)
    for verdict, where, detail in report:
        print(f"  {verdict:<12} {where:<{width}}  {detail}")

    tally = {v: verdicts.count(v) for v in ("PASS", "FAIL", "SKIP", "UNPUBLISHED")}
    print(f"\n  {tally['PASS']} published copies verified, {tally['FAIL']} "
          f"drifted, {tally['SKIP']} unreachable, {tally['UNPUBLISHED']} "
          f"not published\n  (LinkedIn has no anonymous read path; see "
          f"outreach/syndication.md)")
    if tally["FAIL"] or (strict and (tally["SKIP"] or tally["UNPUBLISHED"])):
        print("\nA correction that did not reach the published copy is the "
              "reason this file exists.\nRe-run scripts/gen_syndication.py, "
              "then re-paste the body and Publish.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
