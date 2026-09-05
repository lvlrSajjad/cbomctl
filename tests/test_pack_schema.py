"""Packs must validate against the published JSON schema.

The schema is a separate artifact other tools may consume, so it cannot be
allowed to drift away from the packs it describes.
"""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "policy-packs" / "schema" / "pack.schema.json"
PACKS = sorted((ROOT / "policy-packs" / "packs").glob("*.yaml"))


def test_packs_exist():
    assert len(PACKS) == 6


def _as_json(value):
    """YAML gives real `date` objects; the schema describes the JSON form."""
    import datetime

    if isinstance(value, dict):
        return {k: _as_json(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_as_json(v) for v in value]
    if isinstance(value, datetime.date):
        return value.isoformat()
    return value


@pytest.mark.parametrize("path", PACKS, ids=lambda p: p.stem)
def test_pack_validates_against_published_schema(path):
    schema = json.loads(SCHEMA.read_text())
    jsonschema.validate(_as_json(yaml.safe_load(path.read_text())), schema)


@pytest.mark.parametrize("path", PACKS, ids=lambda p: p.stem)
def test_pack_id_matches_filename(path):
    assert yaml.safe_load(path.read_text())["id"] == path.stem


@pytest.mark.parametrize("path", PACKS, ids=lambda p: p.stem)
def test_a_recommendation_never_describes_itself_as_a_mandate(path):
    """The review found drafts calling BSI and ANSSI guidance "mandatory".

    Scoped to the binding rather than to the whole file: ANSSI's security-visa
    rule quotes its source's own "mandatory hybridation", which is correct --
    it *is* a certification requirement. Banning the word outright would have
    forced a paraphrase of a primary source, which is worse than the problem.
    """
    for rule in yaml.safe_load(path.read_text())["rules"]:
        if rule["binding"] != "guideline_recommendation":
            continue
        text = f"{rule['description']} {rule.get('rationale_note', '')}".lower()
        for word in ("mandator", "must ", "obliged", "required to"):
            assert word not in text, (
                f"{path.stem}/{rule['id']} is a guideline_recommendation but "
                f"its own text says {word!r}")


@pytest.mark.parametrize("path", PACKS, ids=lambda p: p.stem)
def test_verified_rules_quote_their_source(path):
    """A verified rule carries the sentence it was verified against, so a
    reviewer can check the reading without re-fetching the PDF."""
    for rule in yaml.safe_load(path.read_text())["rules"]:
        if rule["status"] != "verified":
            continue
        blob = f"{rule['description']} {rule.get('rationale_note', '')}"
        assert '"' in blob or "\u201c" in blob, (
            f"{path.stem}/{rule['id']} claims verified but quotes nothing")
