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
def test_no_pack_claims_a_mandate_it_does_not_have(path):
    """The review found drafts calling BSI and ANSSI guidance 'mandatory'."""
    text = path.read_text().lower()
    for rule in yaml.safe_load(path.read_text())["rules"]:
        if rule["binding"] == "guideline_recommendation":
            assert "mandator" not in rule["description"].lower()
            assert "must " not in rule["description"].lower()
    assert "mandatory" not in text
