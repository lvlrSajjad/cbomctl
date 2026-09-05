"""Input detection. Raw CycloneDX is primary; the sbom-tools adapter is opt-in."""

from __future__ import annotations

from pathlib import Path

from cbomctl.loader import cyclonedx, sbom_tools
from cbomctl.loader.cyclonedx import CbomParseError, load
from cbomctl.models import CryptoAsset

__all__ = ["CbomParseError", "load", "read_assets"]


def read_assets(source: str | Path, fmt: str = "auto") -> tuple[list[CryptoAsset], str]:
    doc = load(source)
    if fmt == "sbom-tools" or (fmt == "auto" and sbom_tools.is_sbom_tools(doc)):
        return sbom_tools.to_assets(doc), "sbom-tools"
    if fmt in ("auto", "cyclonedx"):
        if fmt == "auto" and not cyclonedx.is_cyclonedx(doc):
            raise CbomParseError(
                "input is neither a CycloneDX document nor recognisable "
                "sbom-tools output; pass --from to force a reader"
            )
        return cyclonedx.to_assets(doc), "cyclonedx"
    raise CbomParseError(f"unknown input format: {fmt}")
