#!/usr/bin/env python3
"""Derive every number the prose claims about a fixture, a pack or the code.

`check_commands.py` closed the gap for *commands*: a line a reader will copy is
executed, or it is annotated unverified. This file closes the same gap for
*counts*. "56 components, 22 of asset type `algorithm`", "8 of 22 unresolved —
more than a third", "five EC keys are tagged `pke`" — every one of those is a
fact about a file in this repository, and until now nothing derived any of them.
Two were found wrong by hand on 2026-09-06 and fixed in `76ca56f`. Running this
file for the first time found three more numbers that hand-checking had missed,
and writing the claim list found five stale *statements* about the packs — a
README declaring "no pack is verified yet" nine months after all seven were.

Generate or parse?
------------------
`gen_article_blocks.py` regenerates blocks that claim to be output, and
generating these table rows the same way would be more in keeping with the
repo. It was tried and rejected, for three reasons that are about where these
numbers actually live:

  * They live in **sentences**, not only in table cells. "It appears in 12
    components; in 11 it is the only function recorded" and "more than a third
    of a real Keycloak CBOM" carry the argument of the page. Generating them
    means either marking fragments mid-sentence or rewriting the prose into
    generated blocks, and the second one flattens the argument each page is
    making into a table.
  * Of the six stale numbers standing when this file was written, **four were
    in prose** — a PROVENANCE table cell written as a sentence, a module
    docstring in `src/`, and two pack-status claims. A generator reaches none
    of those. A docstring in `src/` is not generable at all.
  * A generated block silently rewrites itself. That is right for tool output,
    where the output *is* the truth. It is wrong for a sentence whose
    surrounding argument may no longer hold once the number moves: if `pke` on
    EC keys ever became 1, "reports four Keycloak EC keys as HNDL exposures"
    should stop the build and make someone reread the paragraph, not quietly
    become "reports one".

So: parse. The objection to parsing is that it rots — reword the sentence and
the check silently stops applying, which is exactly the third state this repo
refuses to have. That is fixed by making a claim site mandatory: **a pattern
that matches nothing is a failure**, with the same weight as a wrong number.
Reword the sentence and the checker tells you which claim lost its anchor.

Two sources of truth, deliberately kept apart
---------------------------------------------
Claims about *what the generator emitted* (`56 components`, `6 / 22 carry no
cryptoFunctions`) are derived straight from the fixture JSON. Claims about
*what cbomctl makes of it* (`8 of 22 unresolved`) are derived through the
loader. Deriving the first group through the loader would let a normalizer bug
rewrite the description of the input it was supposed to be normalizing.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

FIXTURES = ROOT / "tests" / "fixtures"

#: Number words the prose actually uses. Deliberately not a general parser:
#: an unrecognised word should fail loudly rather than resolve to something.
WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
    "first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5, "sixth": 6,
    "seventh": 7, "eighth": 8, "ninth": 9, "tenth": 10,
    "no": 0, "none": 0, "zero": 0,
}


def to_int(text: str) -> int | None:
    text = text.strip().lower().replace(",", "")
    if text.isdigit():
        return int(text)
    return WORDS.get(text)


# --------------------------------------------------------------------------
# Derivations
# --------------------------------------------------------------------------

def _algorithms(doc: dict) -> list[dict]:
    return [c for c in doc["components"]
            if c.get("cryptoProperties", {}).get("assetType") == "algorithm"]


def _props(component: dict) -> dict:
    return component.get("cryptoProperties", {}).get("algorithmProperties", {})


def derive() -> dict[str, int]:
    """Every number the prose is allowed to state, and where it comes from."""
    from cbomctl.loader.cyclonedx import load, to_assets
    from cbomctl.policy.schema import available, load_pack

    keycloak = json.loads((FIXTURES / "cbomkit-keycloak.json").read_text())
    kafka = json.loads((FIXTURES / "cbomkit-kafka.json").read_text())
    algs = _algorithms(keycloak)

    def fns(c: dict) -> list[str] | None:
        return _props(c).get("cryptoFunctions")

    def primitive(c: dict) -> str | None:
        return _props(c).get("primitive")

    # What cbomctl makes of the same file, through the real loader.
    assets = [a for a in to_assets(load(FIXTURES / "cbomkit-keycloak.json"))
              if a.asset_type == "algorithm"]

    # `outreach/syndication.md` states the length of the copy it hands over.
    # A LinkedIn post is a fixed-length artifact — the whole advice about the
    # fold depends on it — so the number is checked, not remembered.
    linkedin = (ROOT / "outreach" / "linkedin"
                / "rsa-2048-and-rsa-3072.txt").read_text()
    article = (ROOT / "docs" / "writing" / "rsa-2048-and-rsa-3072.md").read_text()
    prose = re.sub(r"```.*?```", "", re.sub(
        r"<!--.*?-->", "", re.sub(r"\A---\n.*?\n---\n", "", article, count=1,
                                 flags=re.S), flags=re.S), flags=re.S)

    tool_center = json.loads(
        (FIXTURES / "schemas" / "tool-center-v2.tool.schema.json").read_text())

    packs = [load_pack(p) for p in available()]
    rules = [r for p in packs for r in p.rules]

    return {
        # --- the fixture, as CBOMkit emitted it ---
        "keycloak.components": len(keycloak["components"]),
        "keycloak.algorithms": len(algs),
        "keycloak.no_functions": sum(1 for c in algs if fns(c) is None),
        "keycloak.keygen_only": sum(1 for c in algs if fns(c) == ["keygen"]),
        "keycloak.keygen_any": sum(1 for c in algs if "keygen" in (fns(c) or [])),
        "keycloak.primitive_other": sum(1 for c in algs if primitive(c) == "other"),
        "keycloak.pke_all": sum(1 for c in algs if primitive(c) == "pke"),
        "keycloak.pke_ec": sum(1 for c in algs if primitive(c) == "pke"
                               and c["name"].startswith("EC")),
        "kafka.components": len(kafka["components"]),

        # --- what cbomctl resolves, through the loader ---
        "keycloak.unresolved": sum(1 for a in assets if not a.purpose.is_resolved),

        # --- the policy packs ---
        "packs.count": len(packs),
        "packs.verified": sum(1 for p in packs if p.is_verified),
        "packs.rules": len(rules),
        "packs.unverified_rules": sum(1 for p in packs
                                      for _ in p.unverified_rules),
        "packs.contested_rules": sum(1 for r in rules
                                     if r.interpretation.value == "contested"),

        # --- the syndicated copies ---
        "linkedin.rsa_words": len(linkedin.split()),
        "article.rsa_words": len(prose.split()),

        # --- the third-party schema the Tool Center entry is submitted against ---
        "toolcenter.description_maxlength":
            tool_center["definitions"]["tool"]["properties"]
            ["description"]["maxLength"],
    }


# --------------------------------------------------------------------------
# Claims
# --------------------------------------------------------------------------

class Claim:
    """One place in the repository that states a derived number.

    `pattern` must match at least once in `path`; each of its capture groups
    must equal the correspondingly-named stat. `holds` is for claims that are
    not a bare number — "more than a third" — where what can be checked is
    that the sentence is still true of the derived values.
    """

    def __init__(self, path: str, pattern: str, *stats: str,
                 holds=None, says: str = ""):
        self.path, self.pattern, self.stats = path, pattern, stats
        self.holds, self.says = holds, says

    def check(self, S: dict[str, int], report: list, root: Path = ROOT) -> bool:
        target = root / self.path
        if not target.is_file():
            report.append(("FAIL", self.path, "claim site missing: no such file"))
            return False
        text = target.read_text()
        found = list(re.finditer(self.pattern, text))
        if not found:
            report.append(("FAIL", self.path, (
                f"claim site not found — the prose was reworded, moved or "
                f"deleted, and this check no longer applies to anything. "
                f"Re-anchor or remove it in scripts/check_stats.py.\n"
                f"        pattern: {self.pattern}")))
            return False

        ok = True
        for m in found:
            where = f"{self.path}:{text[:m.start()].count(chr(10)) + 1}"
            for group, name in zip(m.groups(), self.stats):
                written = to_int(group)
                if name not in S:
                    report.append(("FAIL", where, (
                        f"`{name}` is not a derivation; check_stats.py names "
                        f"a statistic nothing computes")))
                    ok = False
                elif written is None:
                    report.append(("FAIL", where, (
                        f"`{group}` is not a number this checker can read; "
                        f"add it to WORDS or write it as a digit")))
                    ok = False
                elif written != S[name]:
                    report.append(("FAIL", where, (
                        f"prose says {group.strip()}, {name} derives "
                        f"{S[name]}{(' — ' + self.says) if self.says else ''}")))
                    ok = False
                else:
                    report.append(("CHECKED", where,
                                   f"{name} = {S[name]}"))
            if self.holds is not None:
                if self.holds(S):
                    report.append(("CHECKED", where,
                                   f"holds — {self.says}"))
                else:
                    report.append(("FAIL", where, (
                        f"the sentence is no longer true of the fixture: "
                        f"{self.says}")))
                    ok = False
        return ok


#: A third is the fraction three documents and the Show HN draft lean on. It is
#: checked as a fraction rather than as "36%", because "more than a third" is
#: what the prose says and 8/22 is what has to keep making it true.
def _more_than_a_third(S: dict[str, int]) -> bool:
    return S["keycloak.algorithms"] < 3 * S["keycloak.unresolved"] \
        <= 1.5 * S["keycloak.algorithms"]


CLAIMS = [
    # ---- docs/purpose.md — the page whose whole argument is these numbers ----
    Claim("docs/purpose.md",
          r"published Keycloak CBOM: (\d+) components, (\d+) of asset type",
          "keycloak.components", "keycloak.algorithms"),
    Claim("docs/purpose.md",
          r"`cryptoFunctions` absent entirely \| (\d+) / (\d+) \|",
          "keycloak.no_functions", "keycloak.algorithms"),
    Claim("docs/purpose.md",
          r"`cryptoFunctions: \[keygen\]` and nothing else \| (\d+) / (\d+) \|",
          "keycloak.keygen_only", "keycloak.algorithms"),
    Claim("docs/purpose.md",
          r"It appears in (\d+) components; in (\d+) it is the only function",
          "keycloak.keygen_any", "keycloak.keygen_only"),
    Claim("docs/purpose.md",
          r"\| `primitive: other` \| (\d+) \|",
          "keycloak.primitive_other"),
    Claim("docs/purpose.md",
          r"\| `primitive: pke` on EC keys \| (\d+) \|",
          "keycloak.pke_ec"),
    Claim("docs/purpose.md",
          r"A (\w+) component is tagged `pke`",
          "keycloak.pke_all",
          says="the ordinal counts every pke component, EC keys included"),
    Claim("docs/purpose.md",
          r"reports (\w+) Keycloak EC keys as harvest-now-decrypt-later",
          "keycloak.pke_ec"),
    Claim("docs/purpose.md",
          r"more than a third of a real Keycloak\s+CBOM",
          holds=_more_than_a_third,
          says="unresolved algorithm components are more than a third of them"),

    # ---- the three documents that lean on 8 of 22 ----
    Claim("README.md",
          r"published Keycloak CBOM, (\d+) of (\d+)\n  algorithm components",
          "keycloak.unresolved", "keycloak.algorithms"),
    Claim("README.md", r"more than a third", holds=_more_than_a_third,
          says="unresolved algorithm components are more than a third of them"),
    Claim("docs/index.md",
          r"published Keycloak CBOM, (\d+) of (\d+)\nalgorithm components",
          "keycloak.unresolved", "keycloak.algorithms"),
    Claim("outreach/show-hn.md",
          r"CBOM, (\d+) of (\d+) algorithm components don't say",
          "keycloak.unresolved", "keycloak.algorithms"),
    Claim("outreach/show-hn.md",
          r'"(\d+) of (\d+) components',
          "keycloak.unresolved", "keycloak.algorithms"),

    # ---- docs/DESIGN.md §5 and §13 ----
    Claim("docs/DESIGN.md", r"\((\d+) algorithm components\):",
          "keycloak.algorithms"),
    Claim("docs/DESIGN.md", r"`cryptoFunctions` absent \| (\d+) / (\d+) \|",
          "keycloak.no_functions", "keycloak.algorithms"),
    Claim("docs/DESIGN.md",
          r"`cryptoFunctions: \[keygen\]` only \| (\d+) \|[^|]*it appears in "
          r"(\d+), alone in (\d+)",
          "keycloak.keygen_only", "keycloak.keygen_any", "keycloak.keygen_only"),
    Claim("docs/DESIGN.md", r"\| `primitive: other` \| (\d+) \|",
          "keycloak.primitive_other"),
    Claim("docs/DESIGN.md", r"\| `primitive: pke` on EC keys \| (\d+) \|",
          "keycloak.pke_ec"),
    Claim("docs/DESIGN.md", r"would report (\w+) Keycloak EC keys as HNDL",
          "keycloak.pke_ec"),
    Claim("docs/DESIGN.md",
          r"`cbomkit-keycloak\.json` \| real CBOMkit output, (\d+) components",
          "keycloak.components"),
    Claim("docs/DESIGN.md",
          r"`cbomkit-kafka\.json` \| real CBOMkit output, (\d+) components",
          "kafka.components"),

    # ---- fixture provenance ----
    Claim("tests/fixtures/PROVENANCE.md",
          r"example\)\. (\d+) components\.",
          "keycloak.components"),
    Claim("tests/fixtures/PROVENANCE.md",
          r"(\d+) of (\d+) algorithm components carry no `cryptoFunctions`",
          "keycloak.no_functions", "keycloak.algorithms"),
    Claim("tests/fixtures/PROVENANCE.md",
          r"and (\w+) EC keys are tagged `pke` \(a (\w+) `pke` component is "
          r"RSA-2048\)",
          "keycloak.pke_ec", "keycloak.pke_all"),
    Claim("tests/fixtures/PROVENANCE.md",
          r"same repo\. (\d+) components\.",
          "kafka.components"),

    # ---- the module docstring that states the same statistics ----
    # Not prose a reader copies, but the same numbers making the same
    # argument, in the file that acts on them. It was stale for exactly as
    # long as the docs were.
    Claim("src/cbomctl/normalize/purpose.py",
          r"of (\d+) algorithm components: (\d+) carry no ``cryptoFunctions``",
          "keycloak.algorithms", "keycloak.no_functions"),
    Claim("src/cbomctl/normalize/purpose.py",
          r"``keygen`` appears (\d+) times",
          "keycloak.keygen_any"),
    Claim("src/cbomctl/normalize/purpose.py",
          r"and (\w+) EC keys that\n",
          "keycloak.pke_ec"),
    Claim("src/cbomctl/normalize/purpose.py",
          r"reports (\w+) Keycloak EC keys as harvest-now-decrypt-later",
          "keycloak.pke_ec"),

    # ---- policy packs ----
    Claim("policy-packs/README.md",
          r"There is (\w+) contested rule today",
          "packs.contested_rules"),
    Claim("policy-packs/README.md",
          r"\*\*All (\w+) packs are verified against primary sources\*\*",
          "packs.verified"),
    Claim("policy-packs/README.md",
          r"and (\d+) rules across\n> (\d+) packs ship `status: needs_verification`",
          "packs.unverified_rules", "packs.count"),
    # ---- the syndicated copies ----
    Claim("outreach/syndication.md",
          r"\n(\d+) words, two hashtags, link at the end",
          "linkedin.rsa_words"),
    Claim("outreach/syndication.md",
          r"The article is 1,500 words and lives on your site",
          holds=lambda S: 1350 <= S["article.rsa_words"] <= 1650,
          says="the article is within 10% of the 1,500 words claimed"),

    # ---- the CycloneDX Tool Center entry ----
    Claim("outreach/cyclonedx-tool-center-pr.md",
          r"`tool\.description` has a `maxLength` of (\d+)",
          "toolcenter.description_maxlength",
          says="read from the vendored copy of their schema"),

    Claim("docs/policy-sources.md",
          r"\*\*All (\w+) packs are verified against primary sources\.\*\*",
          "packs.verified"),
    Claim("README.md",
          r"All (\w+) policy packs are read from their primary",
          "packs.verified"),
    Claim("docs/DESIGN.md",
          r"\*\*all (\w+) packs\n> are now verified from primary sources\*\*",
          "packs.verified"),
    Claim("docs/DESIGN.md",
          r"`eu-roadmap`, `nist-ir8547` — (\d+) of them, all verified",
          "packs.count"),
]


def main() -> int:
    S = derive()
    report: list[tuple[str, str, str]] = []
    ok = True
    for claim in CLAIMS:
        ok &= claim.check(S, report)

    width = max((len(w) for _, w, _ in report), default=0)
    for verdict, where, detail in report:
        print(f"  {verdict:<8} {where:<{width}}  {detail}")

    checked = sum(1 for v, _, _ in report if v == "CHECKED")
    failed = sum(1 for v, _, _ in report if v == "FAIL")
    print(f"\n  {checked} claims derived and matched, {failed} failing, "
          f"across {len(CLAIMS)} claim sites and {len(S)} derivations")
    if failed:
        print("\nA number in the prose is a claim about a file in this repository.\n"
              "Either the prose is stale, or the fixture moved and the sentence\n"
              "around the number needs rereading.")
        ok = False
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
