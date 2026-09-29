"""Optional adapter for `sbom-tools` normalized JSON.

**Where the payload comes from.** `sbom-tools convert --to normalized <file>`
emits it from their CLI; it is byte-identical to what their C ABI
(`sbom_tools_parse_sbom_path_json` / `..._str_json`) and the `parse` helpers in
their Python, Node, Go and Swift bindings return. The CLI route was added in
`sbom-tool/sbom-tools#367` (`a393479`) at our request in #366, and is on their
`main` but in no release yet: v0.2.0 predates it. `sbom-tools view -o json` is
*not* this payload — it is a curated projection with nothing derived from
`cryptoProperties`, and feeding it here yields zero assets.

**The shape, as captured from a run of their binary.** The top level is
`document`, `components`, `edges`, `extensions`, `content_hash`,
`primary_component_id`, `collision_count`. Each entry of `components` is
`{canonical_id, component}`; the component carries snake_case fields, `Option`
fields as null, and `crypto_properties` omitted when it has none — the last
three as the maintainer described in #362. The CycloneDX `bom-ref` survives as
`component.identifiers.format_id`. Until 2026-09-29 this module read a flat
list of components with a top-level `bom_ref`, inferred from their structs; it
matched our constructed fixture and read zero assets from real output.

**How firm the contract is**, per #362: their ABI snapshot tests pin only the
*top-level* keys of each payload, in their
`tests/fixtures/abi/contract_required_keys.json`; nested shape, including the
`{canonical_id, component}` wrapper and everything under `crypto_properties`,
is not test-pinned. No schema version is separate from the crate version, and
pre-1.0 a breaking JSON change is permitted in a minor release, listed under
*Upgrade notes* in their CHANGELOG. Pin their version and read the upgrade
notes on each bump. This adapter stays opt-in behind `--from sbom-tools` for
that reason; raw CycloneDX is the supported path, and the maintainer's own
advice was to parse raw CycloneDX rather than their JSON.

**What does not survive the trip**, each confirmed by feeding the same CBOM
through both paths (`sbom-tools-source.json` in the fixtures):

- Source locations. Their parser does not keep `evidence.occurrences`, so every
  row's `locations` is empty. Verdicts are unaffected; the pointer into the
  code is gone.
- An absent `primitive` and an explicit `primitive: "unknown"` both arrive as
  `Unknown`, so this path cannot tell a generator that omitted the field from
  one that said it did not know. Both resolve to Purpose.UNKNOWN; no verdict
  changes, but the diagnostic is gone.
- CycloneDX 1.6's `curve`. Their parser reads only 1.7's `ellipticCurve`, so
  `elliptic_curve` is null for every 1.6 CBOM — all four curves in the real
  CBOMkit Keycloak output are dropped. Verdicts survive only because
  `identity.parse_curve` falls back to the name (`EC-secp384r1`); an asset
  whose name does not carry its curve loses it on this path.

For every CBOM in `tests/fixtures`, against all seven packs, the JSON verdict
through this path equals the one from the raw CycloneDX apart from
`locations` — checked by hand on 2026-09-29 with sbom-tools built at
`a393479`. Only `sbom-tools-source.json` is pinned by a test, since CI cannot
run sbom-tools; the other captures were not committed.
"""

from __future__ import annotations

from typing import Any

from cbomctl.models import CryptoAsset
from cbomctl.normalize import identity, purpose as purpose_mod
from cbomctl.normalize.oids import lookup as oid_lookup

#: snake_case -> CycloneDX camelCase for the fields we consume.
_PRIMITIVE_FROM_RUST = {
    "Ae": "ae", "BlockCipher": "block-cipher", "StreamCipher": "stream-cipher",
    "Hash": "hash", "Mac": "mac", "Signature": "signature", "Pke": "pke",
    "Kem": "kem", "Kdf": "kdf", "KeyAgree": "key-agree", "Xof": "xof",
    "Drbg": "drbg", "Combiner": "combiner", "Unknown": "unknown",
}
_FUNCTION_FROM_RUST = {
    "Encrypt": "encrypt", "Decrypt": "decrypt", "Sign": "sign", "Verify": "verify",
    "Encapsulate": "encapsulate", "Decapsulate": "decapsulate", "Digest": "digest",
    "Tag": "tag", "Keyderive": "keyderive", "KeyDerive": "keyderive",
    "Keygen": "keygen", "Generate": "generate", "Other": "other", "Unknown": "unknown",
}


def _components(doc: dict[str, Any]) -> list[dict[str, Any]]:
    """The component records, unwrapped from their `{canonical_id, component}`
    entries. That wrapper is the real shape of `components[]`; a flat list of
    components was what we inferred from their structs, and nothing emits it.
    """
    comps = doc.get("components")
    if not isinstance(comps, list):
        return []
    return [e["component"] for e in comps
            if isinstance(e, dict) and isinstance(e.get("component"), dict)]


def is_sbom_tools(doc: dict[str, Any]) -> bool:
    return any("crypto_properties" in c for c in _components(doc))


def _bom_ref(comp: dict[str, Any], raw_name: str) -> str:
    """The CycloneDX `bom-ref` survives as `identifiers.format_id`."""
    ids = comp.get("identifiers") or {}
    canonical = comp.get("canonical_id") or {}
    return ids.get("format_id") or canonical.get("value") or raw_name


def _norm(value: Any, table: dict[str, str]) -> str | None:
    if value is None:
        return None
    if isinstance(value, dict):  # externally tagged enum, e.g. {"Other": "..."}
        value = next(iter(value), None)
    return table.get(str(value), str(value).lower())


def to_assets(doc: dict[str, Any]) -> list[CryptoAsset]:
    assets: list[CryptoAsset] = []
    for comp in _components(doc):
        cp = comp.get("crypto_properties")
        if not isinstance(cp, dict):
            continue
        algo = cp.get("algorithm_properties") or {}
        raw_name = comp.get("name") or "<unnamed>"
        primitive = _norm(algo.get("primitive"), _PRIMITIVE_FROM_RUST)
        functions = [_norm(f, _FUNCTION_FROM_RUST)
                     for f in (algo.get("crypto_functions") or [])]
        oid = cp.get("oid")

        curve = identity.parse_curve(raw_name, algo.get("elliptic_curve"))
        res = purpose_mod.resolve(
            raw_name=raw_name,
            crypto_functions=[f for f in functions if f],
            primitive=primitive,
            oid=oid,
        )
        entry = oid_lookup(oid)
        param = algo.get("parameter_set_identifier")
        assets.append(CryptoAsset(
            bom_ref=_bom_ref(comp, raw_name),
            raw_name=raw_name,
            algorithm=(algo.get("algorithm_family")
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
                declared=algo.get("classical_security_level"),
                key_size=identity.parse_key_size(raw_name, param),
                curve=curve,
            ),
            parameter_set=param if param and not str(param).isdigit() else None,
            curve=curve,
            oid=oid,
            asset_type=str(cp.get("asset_type") or "algorithm").lower(),
            spec_version="sbom-tools",
        ))
    return assets
