"""User-supplied facts a CBOM cannot contain.

The load-bearing one is data lifetime. No inventory tool can derive how long
data must stay confidential, and without it there is nothing to rank by.
"""

from __future__ import annotations

import fnmatch
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

from cbomctl.models import CryptoAsset, Purpose

CONFIG_PROPERTY_PREFIX = "cbomctl:"


class AssetRule(BaseModel):
    match: dict[str, str] = Field(default_factory=dict)
    data_lifetime_years: float | None = None
    verification_lifetime_years: float | None = None
    purpose: Purpose | None = None


class Defaults(BaseModel):
    data_lifetime_years: float = 5.0
    migration_years: float = 3.0
    verification_lifetime_years: float | None = None


class Config(BaseModel):
    version: int = 1
    defaults: Defaults = Field(default_factory=Defaults)
    system_category: str | None = None
    assets: list[AssetRule] = Field(default_factory=list)

    @classmethod
    def load(cls, path: str | Path | None) -> "Config":
        if path is None:
            return cls()
        p = Path(path)
        if not p.is_file():
            raise FileNotFoundError(f"config not found: {path}")
        data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        return cls.model_validate(data)

    def _matches(self, rule: AssetRule, asset: CryptoAsset) -> bool:
        for key, pattern in rule.match.items():
            if key == "location":
                files = [loc.file or "" for loc in asset.locations]
                if not any(fnmatch.fnmatch(f, pattern) for f in files):
                    return False
            elif key == "algorithm":
                if (asset.algorithm or "").upper() != pattern.upper():
                    return False
            elif key == "bom_ref":
                if asset.bom_ref != pattern:
                    return False
            elif key == "purpose":
                if asset.purpose.value != pattern:
                    return False
            else:
                return False
        return bool(rule.match)

    def for_asset(self, asset: CryptoAsset) -> tuple[float, str, Purpose | None]:
        """Return (lifetime_years, source, purpose_override).

        Signatures use verification lifetime where one is supplied: what matters
        for a signature is how long it stays trusted, not how long the data it
        covers stays secret.
        """
        wants_verification = asset.purpose is Purpose.SIGNATURE
        for i, rule in enumerate(self.assets):
            if not self._matches(rule, asset):
                continue
            if wants_verification and rule.verification_lifetime_years is not None:
                return rule.verification_lifetime_years, f"config:assets[{i}].verification_lifetime_years", rule.purpose
            if rule.data_lifetime_years is not None:
                return rule.data_lifetime_years, f"config:assets[{i}].data_lifetime_years", rule.purpose
            if rule.purpose is not None:
                break
        if wants_verification and self.defaults.verification_lifetime_years is not None:
            return self.defaults.verification_lifetime_years, "config:defaults.verification_lifetime_years", None
        return self.defaults.data_lifetime_years, "config:defaults.data_lifetime_years", None


def lifetime_from_properties(component: dict[str, Any]) -> float | None:
    """Read `cbomctl:data_lifetime_years` from CycloneDX component properties."""
    for prop in component.get("properties") or []:
        if not isinstance(prop, dict):
            continue
        name = prop.get("name") or ""
        if name == f"{CONFIG_PROPERTY_PREFIX}data_lifetime_years":
            try:
                return float(prop.get("value"))
            except (TypeError, ValueError):
                return None
    return None
