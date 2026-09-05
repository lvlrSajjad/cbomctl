"""Read a CycloneDX 1.6 / 1.7 CBOM.

1.7 is a superset of 1.6 in the crypto subtree, so one reader serves both.
Unrecognised enum values degrade to UNKNOWN rather than raising: a future 1.8
adding a primitive must not crash a CI gate.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from cbomctl.models import CryptoAsset, Location
from cbomctl.normalize import identity, purpose as purpose_mod
from cbomctl.normalize.oids import lookup as oid_lookup


class CbomParseError(ValueError):
    pass


def load(source: str | Path) -> dict[str, Any]:
    raw = _read(source)
    try:
        doc = json.loads(raw)
    except json.JSONDecodeError as exc:  # pragma: no cover - message path
        raise CbomParseError(f"not valid JSON: {exc}") from exc
    if not isinstance(doc, dict):
        raise CbomParseError("top level of a CBOM must be an object")
    return doc


def _read(source: str | Path) -> str:
    if source == "-":
        import sys

        return sys.stdin.read()
    p = Path(source)
    if not p.is_file():
        raise CbomParseError(f"no such file: {source}")
    return p.read_text(encoding="utf-8")


def is_cyclonedx(doc: dict[str, Any]) -> bool:
    return doc.get("bomFormat") == "CycloneDX" or "specVersion" in doc


def _locations(component: dict[str, Any]) -> list[Location]:
    occurrences = (component.get("evidence") or {}).get("occurrences") or []
    out: list[Location] = []
    for o in occurrences:
        if not isinstance(o, dict):
            continue
        out.append(Location(
            file=o.get("location"),
            line=o.get("line"),
            context=o.get("additionalContext"),
        ))
    return out


def to_assets(doc: dict[str, Any]) -> list[CryptoAsset]:
    spec = str(doc.get("specVersion") or "")
    assets: list[CryptoAsset] = []

    for comp in doc.get("components") or []:
        if not isinstance(comp, dict):
            continue
        cp = comp.get("cryptoProperties")
        if not isinstance(cp, dict):
            continue

        algo = cp.get("algorithmProperties") or {}
        raw_name = comp.get("name") or comp.get("bom-ref") or "<unnamed>"
        primitive = algo.get("primitive")
        functions = algo.get("cryptoFunctions") or []
        oid = cp.get("oid")

        res = purpose_mod.resolve(
            raw_name=raw_name,
            crypto_functions=list(functions) if isinstance(functions, list) else None,
            primitive=primitive,
            oid=oid,
        )

        entry = oid_lookup(oid)
        # 1.7 renamed `curve` to `ellipticCurve`; both may appear.
        curve = identity.parse_curve(
            raw_name, algo.get("ellipticCurve") or algo.get("curve"))
        param = algo.get("parameterSetIdentifier")

        locations = _locations(comp)
        corroborating = [loc.context for loc in locations if loc.context]

        assets.append(CryptoAsset(
            bom_ref=comp.get("bom-ref") or raw_name,
            raw_name=raw_name,
            # `algorithmFamily` is 1.7-only; fall back to the OID's canonical
            # name, then to parsing the free-text name.
            algorithm=(algo.get("algorithmFamily")
                       or (entry.algorithm if entry else None)
                       or identity.family(raw_name)),
            purpose=res.purpose,
            purpose_signal=res.signal,
            purpose_conflicts=res.conflicts,
            construction=identity.classify_construction(raw_name, primitive),
            quantum_status=identity.classify_quantum(raw_name),
            key_size=identity.parse_key_size(raw_name, param),
            security_strength=identity.security_strength(
                raw_name,
                declared=algo.get("classicalSecurityLevel"),
                key_size=identity.parse_key_size(raw_name, param),
                curve=curve,
            ),
            parameter_set=param if param and not str(param).isdigit() else None,
            curve=curve,
            oid=oid,
            asset_type=cp.get("assetType") or "algorithm",
            locations=locations,
            corroborating=sorted(set(corroborating)),
            spec_version=spec or None,
        ))
    return assets
