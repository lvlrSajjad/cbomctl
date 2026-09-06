"""action.yml must stay publishable to the GitHub Marketplace.

The Marketplace rejects a description of 125 characters or more, and it only
tells you at the moment you tick the publish box on a release — by which point
the tag is cut and the fix costs another release. The limit is invisible in the
file itself, so it is asserted here instead.
"""

from __future__ import annotations

from pathlib import Path

import yaml

ACTION = Path(__file__).resolve().parent.parent / "action.yml"
#: GitHub's limit, observed on the release publish form.
MAX_DESCRIPTION = 125


def _action() -> dict:
    return yaml.safe_load(ACTION.read_text())


def test_description_fits_the_marketplace_limit() -> None:
    desc = _action()["description"].strip()
    assert len(desc) < MAX_DESCRIPTION, (
        f"action.yml description is {len(desc)} characters; the Marketplace "
        f"requires fewer than {MAX_DESCRIPTION}"
    )


def test_marketplace_required_metadata_is_present() -> None:
    """Name, description and branding are all required to publish."""
    action = _action()
    assert action.get("name")
    assert action.get("description")
    branding = action.get("branding") or {}
    assert branding.get("icon"), "branding.icon is required to publish"
    assert branding.get("color"), "branding.color is required to publish"
