"""Every pack against every fixture, checking the invariants hold everywhere.

This exists because each time the pack set grew, running them together
surfaced a bug that no single-pack test caught: an unscoped INFO rule masking
INDETERMINATE, an N/A that should have been PASS, and a parameter conflict that
claimed a stricter target existed while naming none. The combinations are where
the bugs live.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from cbomctl.config import Config
from cbomctl.loader import read_assets
from cbomctl.models import Verdict
from cbomctl.policy.schema import available, load_pack
from cbomctl.verdict.conflicts import detect
from cbomctl.verdict.matrix import build

FIXTURES = sorted((Path(__file__).parent / "fixtures").glob("*.json"))
CATEGORIES = [None, "web-cloud", "high-value-asset", "high-risk",
              "software-firmware-signing"]
TODAY = date(2026, 9, 6)


@pytest.fixture(scope="module")
def packs():
    return [load_pack(p) for p in available()]


def _run(packs, fixture, category):
    assets, _ = read_assets(fixture)
    matrix = build(assets, packs, Config(system_category=category), today=TODAY)
    return matrix, detect(matrix, packs)


@pytest.mark.parametrize("category", CATEGORIES, ids=lambda c: c or "undeclared")
@pytest.mark.parametrize("fixture", FIXTURES, ids=lambda f: f.stem)
class TestInvariants:
    def test_unresolved_purpose_never_passes_or_disappears(
            self, packs, fixture, category):
        """The core promise. If we cannot tell what a key is for, no
        jurisdiction may report PASS or N/A for it."""
        matrix, _ = _run(packs, fixture, category)
        for row in matrix.rows:
            if row.purpose not in ("unknown", "ambiguous"):
                continue
            for jid, cell in row.cells.items():
                assert cell.verdict not in (Verdict.PASS, Verdict.NOT_APPLICABLE), (
                    f"{row.display} is {row.purpose} but {jid} says "
                    f"{cell.verdict.value}")

    def test_a_recommendation_never_produces_fail(self, packs, fixture, category):
        matrix, _ = _run(packs, fixture, category)
        for row in matrix.rows:
            for jid, cell in row.cells.items():
                if cell.verdict is not Verdict.FAIL:
                    continue
                assert any(r.binding.is_mandatory for r in cell.rules), (
                    f"{jid} FAILs {row.display} with no mandatory rule")

    def test_every_conflict_states_its_trade(self, packs, fixture, category):
        """A conflict with no resolution must say so in as many words. Silence
        reads as 'resolved', which is the opposite of the truth."""
        _, conflicts = _run(packs, fixture, category)
        for c in conflicts:
            assert c.cost_note, f"{c.id} has no cost note"
            if c.satisfies_all is None:
                assert "no single configuration" in c.cost_note.lower(), (
                    f"{c.id} names no satisfies-all target and does not say so")

    def test_output_is_deterministic(self, packs, fixture, category):
        from cbomctl.report import json_out

        a = json_out.render(*_run(packs, fixture, category))
        b = json_out.render(*_run(packs, fixture, category))
        assert a == b
