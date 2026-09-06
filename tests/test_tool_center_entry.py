"""The Tool Center entry in `outreach/` must validate before it is submitted.

`outreach/cyclonedx-tool-center-pr.md` carries the exact JSON that goes into
`tools/cbomctl.json` on a PR to CycloneDX/tool-center. It was validated once by
hand (`a8fa87b`) against a copy of their schema in `.research/`, which is
gitignored — so nothing could re-validate it, and the file has been edited
since. Their `validate_tools` workflow will run this check on the PR; running
it here means finding out before a third party does.

**Vendored, not fetched.** `ci.yml`'s `cbom-schema-conformance` job fetches the
CycloneDX BOM schemas on every run, and that is right for it: those fixtures
claim to be valid CycloneDX *as the spec stands*, so upstream movement is the
signal. This is a different claim. What has to hold is that the entry validates
against the schema their CI will use, and the useful property is that
`./scripts/check.sh` and a bare `pytest -q` prove it offline, on a laptop with
no network, the same way every other test in this suite does. Upstream drift is
still worth knowing about, so `ci.yml` diffs the vendored copy against
`schemas/tool.schema.json` on `main` — that failure names the schema, which is
the right thing to look at, rather than failing here and naming our entry.

Vendored copy: CycloneDX/tool-center `schemas/tool.schema.json`, as of commit
`fb39a9915635` (2025-11-13), fetched 2026-09-06. draft-07, `$id`
`https://cyclonedx.org/schema/tool-center-v2.tool.schema.json`. The copy served
at that `$id` is byte-for-byte the same document once parsed, minified.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import jsonschema
import pytest

ROOT = Path(__file__).resolve().parents[1]
DRAFT = ROOT / "outreach" / "cyclonedx-tool-center-pr.md"
SCHEMA = ROOT / "tests" / "fixtures" / "schemas" / "tool-center-v2.tool.schema.json"


def entry() -> dict:
    """The one ```json fence under `## File contents`."""
    body = DRAFT.read_text().split("## File contents", 1)[1]
    m = re.search(r"```json\n(.*?)```", body, re.S)
    assert m, "no ```json fence under `## File contents` in the PR draft"
    return json.loads(m.group(1))


@pytest.fixture(scope="module")
def schema() -> dict:
    return json.loads(SCHEMA.read_text())


def test_the_entry_validates(schema):
    jsonschema.validate(entry(), schema)


def test_the_entry_declares_the_schema_it_is_validated_against(schema):
    """`$schema` in the entry is what MetaConfigurator and a reviewer resolve.
    If it points somewhere else, this test is validating a different document
    from the one they will."""
    assert entry()["$schema"] == schema["$id"]


def test_the_description_fits(schema):
    """The first draft ran to 312 characters against a `maxLength` of 250 and
    would have been bounced by their `validate_tools` workflow. The bound is
    read from the schema, not repeated here."""
    limit = schema["definitions"]["tool"]["properties"]["description"]["maxLength"]
    assert len(entry()["tool"]["description"]) <= limit


def test_a_value_outside_their_enums_is_rejected(schema):
    """A check that cannot fail is not a check. Every enum in this entry was
    typed by hand from their schema; this is the failure that catches a typo."""
    bad = entry()
    bad["tool"]["analysis"] = ["POLICY_EVALUATON"]        # sic
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(bad, schema)


def test_an_over_long_description_is_rejected(schema):
    bad = entry()
    bad["tool"]["description"] = "x" * 251
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(bad, schema)


def test_the_prose_around_the_entry_names_the_fields_it_uses(schema):
    """The draft argues for specific enum values in prose — `capabilities: CBOM`,
    `analysis: POLICY_EVALUATION`. Those sentences are what a maintainer reads
    first, and they drifted from the JSON once already."""
    text = DRAFT.read_text()
    tool = entry()["tool"]
    for field in ("capabilities", "analysis"):
        for value in tool[field]:
            assert f"{field}: {value}" in text or f'{field}: ["{value}"]' in text, (
                f"the prose does not mention `{field}: {value}`, which the "
                f"entry claims")
