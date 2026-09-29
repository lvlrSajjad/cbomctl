#!/usr/bin/env python3
"""Generate `docs/llms.txt` from the site navigation in `mkdocs.yml`.

`llms.txt` (https://llmstxt.org) is a plain index an agent can read instead of
crawling rendered pages. It is a list of pages, and a hand-kept list of pages
drifts the first time a page is added or renamed — so it is derived from the
same nav the site is built from, and CI fails if it is stale.

MkDocs copies non-Markdown files in `docs/` to the site verbatim, so this is
served at `<site_url>llms.txt`. On a GitHub project page that is a subpath, not
the domain root the proposal names; there is no root to publish to.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
MKDOCS = ROOT / "mkdocs.yml"
OUT = ROOT / "docs" / "llms.txt"


class _Loader(yaml.SafeLoader):
    """Safe loading, with `!!python/name:` tags read as plain strings.

    mkdocs.yml names a superfences formatter by Python path. Only the nav and
    the site fields are needed here, so nothing is imported.
    """


_Loader.add_multi_constructor(
    "tag:yaml.org,2002:python/", lambda loader, suffix, node: None)


def page_url(site_url: str, md_path: str) -> str:
    """The rendered URL MkDocs gives `md_path` with `use_directory_urls` on."""
    stem = md_path.removesuffix(".md")
    if stem == "index":
        return site_url
    if stem.endswith("/index"):
        return f"{site_url}{stem.removesuffix('index')}"
    return f"{site_url}{stem}/"


def walk(nav: list, site_url: str, section: str | None, out: dict) -> None:
    for item in nav:
        ((title, target),) = item.items()
        if isinstance(target, list):
            walk(target, site_url, section or title, out)
        else:
            out.setdefault(section or "Docs", []).append(
                f"- [{title}]({page_url(site_url, target)})")


def render() -> str:
    cfg = yaml.load(MKDOCS.read_text(), Loader=_Loader)
    site_url = cfg["site_url"].rstrip("/") + "/"
    sections: dict[str, list[str]] = {}
    walk(cfg["nav"], site_url, None, sections)

    lines = [
        f"# {cfg['site_name']}",
        "",
        f"> {' '.join(cfg['site_description'].split())}",
        "",
        "Install: `pip install cbomctl`. Every policy rule cites the section or "
        "page of its primary source; verdicts are not compliance advice.",
        "",
    ]
    for name, links in sections.items():
        lines += [f"## {name}", "", *links, ""]
    lines += [
        "## Optional",
        "",
        f"- [Source code]({cfg['repo_url']})",
        "- [PyPI package](https://pypi.org/project/cbomctl/)",
        f"- [Changelog]({cfg['repo_url']}/blob/main/CHANGELOG.md)",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    content = render()
    if "--check" in sys.argv:
        if not OUT.is_file() or OUT.read_text() != content:
            print("stale docs/llms.txt (run scripts/gen_llms_txt.py)")
            return 1
        print("checked docs/llms.txt")
        return 0
    OUT.write_text(content)
    print("wrote docs/llms.txt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
