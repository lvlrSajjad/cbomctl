"""`scripts/check_commands.py` must reject the fiction it was written for.

`scripts/check.sh` opens with the reason this file exists: a check that cannot
fail is not a check. `check_commands.py` reports green over a repository whose
docs are already correct, which proves nothing on its own. So each case here
writes a document containing one specific lie and asserts the checker catches
it — starting with the exact quickstart line that prompted the whole exercise.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

_spec = importlib.util.spec_from_file_location(
    "check_commands", ROOT / "scripts" / "check_commands.py")
cc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cc)


def run_on(tmp_path: Path, name: str, text: str) -> tuple[bool, str]:
    """Point the checker at one throwaway document; return (ok, report)."""
    doc = tmp_path / name
    doc.write_text(text)
    cwd = cc.scratch()
    report: list[tuple[str, str, str]] = []
    ok = True
    try:
        for b in cc.blocks(doc):
            ok &= cc.check_block(b, cwd, report)
    finally:
        import shutil
        shutil.rmtree(cwd, ignore_errors=True)
    return ok, "\n".join(f"{v} {w} {d}" for v, w, d in report)


def test_the_quickstart_pipeline_that_started_this_is_rejected(tmp_path):
    """`sbom-tools view -o json | cbomctl verdict -` shipped for four releases.

    It could never have worked: that projection carries no crypto fields. The
    checker has to refuse it — both because it is not a bare `cbomctl` call and
    because nothing here can run `sbom-tools`.
    """
    ok, report = run_on(tmp_path, "quickstart.md", """# Q

```bash
sbom-tools view app-cbom.cdx.json -o json | cbomctl verdict - --from sbom-tools
```
""")
    assert not ok
    assert "sbom-tools view" in report


def test_a_flag_the_cli_does_not_have_is_rejected(tmp_path):
    ok, report = run_on(tmp_path, "d.md", """# D

```bash
cbomctl verdict app-cbom.json --jurisdictions bsi-de --no-such-flag
```
""")
    assert not ok, report


def test_a_subcommand_the_cli_does_not_have_is_rejected(tmp_path):
    ok, report = run_on(tmp_path, "d.md", """# D

```bash
cbomctl summarise app-cbom.json
```
""")
    assert not ok, report


def test_a_synopsis_flag_that_does_not_exist_is_rejected(tmp_path):
    """`docs/DESIGN.md` advertised `--strict-unknown` for four releases."""
    ok, report = run_on(tmp_path, "d.md", """# D

<!-- synopsis -->
```
cbomctl verdict <cbom|-> [--strict-unknown]
```
""")
    assert not ok
    assert "--strict-unknown" in report


def test_an_untagged_output_fence_is_rejected(tmp_path):
    """The docs-site landing page carried a hand-edited matrix for four
    releases because nothing required a fence to say what it was."""
    ok, report = run_on(tmp_path, "index.md", """# I

```
ASSET           PURPOSE        bsi-de
X25519MLKEM768  key-agreement  PASS      ⚠ c3,c4
```
""")
    assert not ok
    assert "untagged fence" in report


def test_unverified_without_a_reason_is_rejected(tmp_path):
    ok, report = run_on(tmp_path, "d.md", """# D

<!-- unverified -->
```bash
gh release create v9.9.9
```
""")
    assert not ok
    assert "no reason" in report


def test_unverified_with_a_reason_is_accepted(tmp_path):
    ok, report = run_on(tmp_path, "d.md", """# D

<!-- unverified: pushes a tag; irreversible, and nothing in CI should do it -->
```bash
gh release create v9.9.9
```
""")
    assert ok, report


def test_an_excerpt_that_drifted_from_its_command_is_rejected(tmp_path):
    ok, report = run_on(tmp_path, "d.md", """# D

<!-- excerpt: verdict tests/fixtures/conflict-hybrid.json -j bsi-de -->
```
ECDH  key-agreement  PASS
```
""")
    assert not ok
    assert "does not contain it" in report


def test_an_excerpt_that_holds_is_accepted(tmp_path):
    ok, report = run_on(tmp_path, "d.md", """# D

<!-- excerpt: verdict tests/fixtures/purpose-ambiguous.json -j bsi-de -->
```
└ as key transport → critical · as signature → medium
```
""")
    assert ok, report


def test_a_workflow_input_the_action_does_not_declare_is_rejected(tmp_path):
    """`docs/ci.md` passed `output: cbom.json` to CBOMkit's action, which
    declares no inputs at all. The same mistake against our own action is what
    this catches."""
    ok, report = run_on(tmp_path, "ci.md", """# C

```yaml
steps:
  - uses: lvlrSajjad/cbomctl@v0
    with:
      cbom: cbom.json
      jurisdiction: bsi-de
```
""")
    assert not ok
    assert "jurisdiction" in report


def test_a_workflow_that_matches_the_action_is_accepted(tmp_path):
    ok, report = run_on(tmp_path, "ci.md", """# C

```yaml
steps:
  - uses: lvlrSajjad/cbomctl@v0
    with:
      cbom: cbom.json
      jurisdictions: bsi-de
      format: sarif
```
""")
    assert ok, report


def test_a_tag_this_repo_does_not_have_is_rejected(tmp_path):
    ok, report = run_on(tmp_path, "ci.md", """# C

```yaml
steps:
  - uses: lvlrSajjad/cbomctl@v99
    with: { cbom: cbom.json }
```
""")
    assert not ok
    assert "v99" in report


def test_a_script_that_does_not_exist_is_rejected(tmp_path):
    ok, report = run_on(tmp_path, "d.md", """# D

```bash
./scripts/no-such-script.sh
```
""")
    assert not ok, report


def test_a_flag_in_prose_that_the_cli_does_not_have_is_rejected(tmp_path):
    """`--strict-unknown` appeared three times in docs/DESIGN.md and not once
    inside a fence. Checking only fenced commands would have missed all of
    them."""
    doc = tmp_path / "d.md"
    doc.write_text("Pass `--strict-unknown` to make unknowns exit 3.\n")
    cwd = cc.scratch()
    report: list[tuple[str, str, str]] = []
    try:
        ok = cc.check_prose_flags(doc, cwd, report, cc.cli_help(cwd))
    finally:
        import shutil
        shutil.rmtree(cwd, ignore_errors=True)
    assert not ok
    assert "--strict-unknown" in "\n".join(d for _, _, d in report)


def test_a_flag_belonging_to_another_tool_is_accepted(tmp_path):
    doc = tmp_path / "d.md"
    doc.write_text("open-quantum-secure has `--data-lifetime-years`.\n")
    cwd = cc.scratch()
    report: list[tuple[str, str, str]] = []
    try:
        ok = cc.check_prose_flags(doc, cwd, report, cc.cli_help(cwd))
    finally:
        import shutil
        shutil.rmtree(cwd, ignore_errors=True)
    assert ok, report


def test_the_repositorys_own_prose_declares_every_flag_it_names():
    """Belt and braces for the sweep: run the prose check over the real docs."""
    cwd = cc.scratch()
    report: list[tuple[str, str, str]] = []
    ok = True
    try:
        help_text = cc.cli_help(cwd)
        for base in cc.SEARCH:
            for p in ([base] if base.is_file() else sorted(base.rglob("*.md"))):
                if any(g in p.parents for g in cc.GENERATED):
                    continue
                ok &= cc.check_prose_flags(p, cwd, report, help_text)
    finally:
        import shutil
        shutil.rmtree(cwd, ignore_errors=True)
    assert ok, "\n".join(f"{w} {d}" for v, w, d in report if v == "FAIL")


@pytest.mark.parametrize("doc", sorted(
    p for base in cc.SEARCH
    for p in ([base] if base.is_file() else base.rglob("*.md"))
    if not any(g in p.parents for g in cc.GENERATED)
), ids=lambda p: str(p.relative_to(ROOT)))
def test_every_swept_document_passes(doc):
    """The repository's own prose, one file per test id, so a failure names
    the file rather than dumping the whole sweep."""
    cwd = cc.scratch()
    report: list[tuple[str, str, str]] = []
    ok = True
    try:
        for b in cc.blocks(doc):
            ok &= cc.check_block(b, cwd, report)
    finally:
        import shutil
        shutil.rmtree(cwd, ignore_errors=True)
    assert ok, "\n".join(f"{v} {w} {d}" for v, w, d in report if v == "FAIL")


def test_an_input_a_third_party_action_does_not_declare_is_rejected(tmp_path):
    """The 0.1.4 fix by hand, now a check.

    `docs/ci.md` passed `with: { output: cbom.json }` to `cbomkit-action`,
    which declares no inputs at all. It was corrected by reading their
    `action.yml` and then went straight back to being unchecked, because
    nothing in this file could reach somebody else's repository. It can now.
    """
    ok, report = run_on(tmp_path, "ci.md", """# C

```yaml
steps:
  - uses: cbomkit/cbomkit-action@main
    with:
      output: cbom.json
```
""")
    if "unreachable" in report:
        pytest.skip("github.com unreachable; the check reports SKIP by design")
    assert not ok
    assert "declares none at all" in report


def test_an_env_var_the_third_party_action_does_not_document_is_rejected(tmp_path):
    """A docker action declares no inputs, so `action.yml` cannot catch a
    mistyped `env:` key. Their README documents the names, and that is the
    artifact to check against."""
    ok, report = run_on(tmp_path, "ci.md", """# C

```yaml
steps:
  - uses: cbomkit/cbomkit-action@main
    env:
      CBOMKIT_LANGUAGE: java
```
""")
    if "unreachable" in report:
        pytest.skip("github.com unreachable; the check reports SKIP by design")
    assert not ok
    assert "not documented in" in report


def test_a_third_party_ref_that_does_not_exist_is_rejected(tmp_path):
    ok, report = run_on(tmp_path, "ci.md", """# C

```yaml
steps:
  - uses: cbomkit/cbomkit-action@v99.99.99
    env:
      CBOMKIT_LANGUAGES: java
```
""")
    if "unreachable" in report:
        pytest.skip("github.com unreachable; the check reports SKIP by design")
    assert not ok
    assert "has no action.yml" in report


def test_an_unregistered_third_party_action_is_reported_unchecked(tmp_path):
    """Not a failure — a visible hole. Adding an action to a documented
    workflow should be a decision someone reads, not a silent gap."""
    ok, report = run_on(tmp_path, "ci.md", """# C

```yaml
steps:
  - uses: some-org/some-action@v1
    with:
      whatever: 1
```
""")
    assert ok, report
    assert "add it to THIRD_PARTY_ACTIONS" in report


def test_the_documented_workflow_resolves_every_action_it_names(tmp_path):
    """`docs/ci.md` itself, end to end: our action and all three of theirs."""
    doc = ROOT / "docs" / "ci.md"
    report: list[tuple[str, str, str]] = []
    ok = True
    cwd = cc.scratch()
    try:
        for b in cc.blocks(doc):
            if b.lang in ("yaml", "yml"):
                ok &= cc.check_block(b, cwd, report)
    finally:
        import shutil
        shutil.rmtree(cwd, ignore_errors=True)
    assert ok, "\n".join(f"{v} {w} {d}" for v, w, d in report if v == "FAIL")
    assert "cbomkit/cbomkit-action" in "\n".join(d for _, _, d in report)
