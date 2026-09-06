"""`scripts/check_published.py` must catch a published copy that drifted.

The point of this checker is the one gap `gen_syndication.py --check` cannot
reach: between a corrected file in `outreach/devto/` and the copy a reader
sees on dev.to sits a paste into a browser that may never have happened. So
these cases are about a *published* document disagreeing with the local one —
a body that drifted, a canonical URL that did not save, a post that was taken
down — with `fetch` replaced so nothing here touches the network.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

_spec = importlib.util.spec_from_file_location(
    "check_published", ROOT / "scripts" / "check_published.py")
cp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cp)

ARTICLE = cp.gen.ARTICLES[0]


def published(**overrides) -> dict:
    """What dev.to would return for a correctly published copy."""
    doc = {
        "title": ARTICLE["title"],
        "canonical_url": f"{cp.gen.SITE}/{ARTICLE['slug']}/",
        "tags": [t.strip() for t in ARTICLE["tags"].split(",")],
        "body_markdown": cp.as_published(ARTICLE["out"].read_text()),
    }
    doc.update(overrides)
    return doc


def run(monkeypatch, doc, article=None) -> tuple[str, str]:
    monkeypatch.setattr(cp, "fetch", lambda _url: doc)
    report: list[tuple[str, str, str]] = []
    verdict = cp.check(article or ARTICLE, report)
    return verdict, "\n".join(f"{v} {w} {d}" for v, w, d in report)


def test_a_correctly_published_copy_passes(monkeypatch):
    verdict, report = run(monkeypatch, published())
    assert verdict == "PASS", report


def test_a_published_body_that_drifted_is_rejected(monkeypatch):
    """The failure this file exists for: the article was corrected in the repo
    and the correction was never pasted."""
    body = published()["body_markdown"].replace(
        "Germany's BSI recommends", "Germany's BSI mandates", 1)
    verdict, report = run(monkeypatch, published(body_markdown=body))
    assert verdict == "FAIL"
    assert "drifted" in report
    assert "mandates" in report


def test_a_missing_canonical_url_is_rejected(monkeypatch):
    """Step 5 of the dev.to instructions is the one that silently does not
    save, and without it dev.to outranks the copy that gets corrected."""
    verdict, report = run(monkeypatch, published(canonical_url=None))
    assert verdict == "FAIL"
    assert "canonical_url" in report


def test_a_retitled_post_is_rejected(monkeypatch):
    verdict, report = run(monkeypatch, published(title="Something else"))
    assert verdict == "FAIL"
    assert "published title" in report


def test_wrong_tags_are_rejected(monkeypatch):
    verdict, report = run(monkeypatch, published(tags=["security"]))
    assert verdict == "FAIL"
    assert "published tags" in report


def test_a_deleted_post_is_rejected(monkeypatch):
    verdict, report = run(monkeypatch, {})
    assert verdict == "FAIL"
    assert "404" in report


def test_an_unreachable_devto_is_skipped_not_passed(monkeypatch):
    """A network failure is not evidence the copy is correct, and it is not a
    reason to redden an unrelated commit either."""
    verdict, report = run(monkeypatch, None)
    assert verdict == "SKIP"
    assert "unreachable" in report


def test_an_article_with_no_recorded_url_is_reported_not_passed(monkeypatch):
    verdict, report = run(monkeypatch, published(), {**ARTICLE, "devto": None})
    assert verdict == "UNPUBLISHED"
    assert "no dev.to URL recorded" in report


def test_only_the_opening_fence_is_normalised():
    """dev.to's editor rewrites a bare opening fence to ```plaintext and leaves
    the closing one bare. Normalising both would hide a real difference, and
    normalising neither would report every article as drifted."""
    assert cp.as_published("a\n```\nx\n```\nb\n") == "a\n```plaintext\nx\n```\nb\n"
    assert cp.as_published("```yaml\nk: v\n```\n") == "```yaml\nk: v\n```\n"


def test_a_url_that_is_not_a_devto_article_is_rejected(monkeypatch):
    verdict, report = run(monkeypatch, published(),
                          {**ARTICLE, "devto": "https://example.com/post"})
    assert verdict == "FAIL"
    assert "not a dev.to article URL" in report


def test_every_recorded_url_resolves_to_the_read_api():
    for a in cp.gen.ARTICLES:
        if a.get("devto"):
            assert cp.api_path(a["devto"]), a["devto"]
