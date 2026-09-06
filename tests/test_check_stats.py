"""`scripts/check_stats.py` must reject the stale numbers it was written for.

Same standard as `tests/test_check_commands.py`: the checker reports green over
a repository whose numbers are already correct, which proves nothing on its
own. Each case here writes a document stating one specific wrong thing about a
fixture and asserts the checker catches it.

The last two are the ones that matter most, because they are the failure mode
that makes people distrust a parsing checker: a claim whose sentence was
reworded, and a claim naming a statistic nothing computes. Either would let the
check quietly stop applying. Both fail.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

_spec = importlib.util.spec_from_file_location(
    "check_stats", ROOT / "scripts" / "check_stats.py")
cs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cs)

S = cs.derive()


def run_on(tmp_path: Path, name: str, text: str, claim: cs.Claim
           ) -> tuple[bool, str]:
    """Point one claim at one throwaway document; return (ok, report)."""
    (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / name).write_text(text)
    report: list[tuple[str, str, str]] = []
    ok = claim.check(S, report, root=tmp_path)
    return ok, "\n".join(f"{v} {w} {d}" for v, w, d in report)


def test_a_number_that_disagrees_with_the_fixture_is_rejected(tmp_path):
    """The exact shape of the two errors fixed in `76ca56f`."""
    ok, report = run_on(
        tmp_path, "d.md",
        "| `cryptoFunctions: [keygen]` and nothing else | 12 / 22 | ... |\n",
        cs.Claim("d.md",
                 r"`cryptoFunctions: \[keygen\]` and nothing else \| (\d+) / (\d+) \|",
                 "keycloak.keygen_only", "keycloak.algorithms"))
    assert not ok
    assert "prose says 12, keycloak.keygen_only derives 11" in report


def test_a_number_written_as_a_word_is_read_and_checked(tmp_path):
    """`five EC keys are tagged pke` was wrong in two files and in one
    docstring, and no digit appeared in any of them."""
    ok, report = run_on(
        tmp_path, "d.md", "and five EC keys are tagged `pke`.\n",
        cs.Claim("d.md", r"and (\w+) EC keys are tagged `pke`",
                 "keycloak.pke_ec"))
    assert not ok
    assert "prose says five" in report

    ok, report = run_on(
        tmp_path, "d.md", "and four EC keys are tagged `pke`.\n",
        cs.Claim("d.md", r"and (\w+) EC keys are tagged `pke`",
                 "keycloak.pke_ec"))
    assert ok, report


def test_a_number_the_checker_cannot_read_is_rejected(tmp_path):
    """`a handful` is not a claim that can be checked, so it is not allowed to
    pass as one."""
    ok, report = run_on(
        tmp_path, "d.md", "and several EC keys are tagged `pke`.\n",
        cs.Claim("d.md", r"and (\w+) EC keys are tagged `pke`",
                 "keycloak.pke_ec"))
    assert not ok
    assert "not a number this checker can read" in report


def test_a_reworded_sentence_loses_its_anchor_and_is_rejected(tmp_path):
    """The whole objection to parsing prose. A pattern that matches nothing is
    a check that has silently stopped existing, so it fails."""
    ok, report = run_on(
        tmp_path, "d.md", "The fixture has a number of EC keys tagged pke.\n",
        cs.Claim("d.md", r"and (\w+) EC keys are tagged `pke`",
                 "keycloak.pke_ec"))
    assert not ok
    assert "claim site not found" in report


def test_a_claim_naming_a_statistic_nothing_derives_is_rejected(tmp_path):
    ok, report = run_on(
        tmp_path, "d.md", "17 widgets.\n",
        cs.Claim("d.md", r"(\d+) widgets", "keycloak.widgets"))
    assert not ok
    assert "is not a derivation" in report


def test_a_claim_site_that_was_deleted_is_rejected(tmp_path):
    report: list[tuple[str, str, str]] = []
    ok = cs.Claim("gone.md", r"(\d+)", "keycloak.components").check(
        S, report, root=tmp_path)
    assert not ok
    assert "claim site missing" in "\n".join(d for _, _, d in report)


def test_a_sentence_that_stopped_being_true_is_rejected(tmp_path):
    """"More than a third" is not a number, so what is checked is whether the
    sentence still holds of the fixture. If unresolved ever dropped to 5 of 22
    the sentence would be false while every digit on the page stayed right."""
    ok, report = run_on(
        tmp_path, "d.md", "more than a third of a real Keycloak CBOM\n",
        cs.Claim("d.md", r"more than a third of a real Keycloak CBOM",
                 holds=lambda S: 3 * 5 > S["keycloak.algorithms"],
                 says="unresolved would have to be more than a third"))
    assert not ok
    assert "no longer true of the fixture" in report

    ok, report = run_on(
        tmp_path, "d.md", "more than a third of a real Keycloak CBOM\n",
        cs.Claim("d.md", r"more than a third of a real Keycloak CBOM",
                 holds=cs._more_than_a_third, says="8 of 22 is 36%"))
    assert ok, report


def test_the_load_bearing_statistic_is_the_one_the_prose_leans_on():
    """`README.md`, `docs/index.md` and the Show HN draft all say "8 of 22 —
    more than a third". If the fixture is ever replaced, this says so in one
    line instead of as thirty claim-site failures."""
    assert S["keycloak.unresolved"] == 8
    assert S["keycloak.algorithms"] == 22
    assert cs._more_than_a_third(S)


def test_every_claim_in_the_repository_holds():
    report: list[tuple[str, str, str]] = []
    ok = True
    for claim in cs.CLAIMS:
        ok &= claim.check(S, report)
    assert ok, "\n".join(f"{w} {d}" for v, w, d in report if v == "FAIL")
