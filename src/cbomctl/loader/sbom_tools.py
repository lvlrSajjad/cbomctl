"""Optional adapter for `sbom-tools` normalized JSON.

The shape is confirmed. The upstream maintainer answered our question in
`sbom-tool/sbom-tools#362`: the normalized payload arrives "snake_case, no
serde renames, `Option` fields as null, and `crypto_properties` itself omitted
when the component has none". That is exactly what this module reads.

**Where the payload comes from — and where it does not.** It is produced by the
C ABI (`sbom_tools_parse_sbom_path_json` / `..._str_json`) and by the `parse`
helpers in their Python, Node, Go and Swift bindings. It is *not* reachable
from their CLI: `sbom-tools view -o json` is a curated projection carrying
`name`, `version`, `ecosystem`, `licenses`, `supplier`, `dependency_kind`,
`vulnerability_count`, `vulnerabilities[]` and EOL fields, and nothing derived
from `cryptoProperties`. Feeding that projection here yields zero assets.

**How firm the contract is**, per the same answer: their ABI snapshot tests pin
only the *top-level* keys of each payload, in their
`tests/fixtures/abi/contract_required_keys.json`; nested shape, including
everything under `crypto_properties`, is not test-pinned. No schema version is
separate from the crate version, and pre-1.0 a breaking JSON change is
permitted in a minor release, listed under *Upgrade notes* in their CHANGELOG.
A consumer of
this path should therefore pin the `sbom-tools` crate version and read the
upgrade notes on each bump. This adapter stays opt-in behind `--from
sbom-tools` for that reason; raw CycloneDX is the supported path, and the
maintainer's own advice was to parse raw CycloneDX rather than their JSON.

Known lossy point, also confirmed upstream: their parser maps an absent
`primitive` and an explicit `primitive: "unknown"` to the same value, so this
path cannot tell a generator that omitted the field from one that said it did
not know. They intend to document that rather than change it. Both still
resolve to Purpose.UNKNOWN, so no verdict changes — but the diagnostic is gone.
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


def is_sbom_tools(doc: dict[str, Any]) -> bool:
    comps = doc.get("components")
    if not isinstance(comps, list) or not comps:
        return False
    return any(isinstance(c, dict) and "crypto_properties" in c for c in comps)


def _norm(value: Any, table: dict[str, str]) -> str | None:
    if value is None:
        return None
    if isinstance(value, dict):  # externally tagged enum, e.g. {"Other": "..."}
        value = next(iter(value), None)
    return table.get(str(value), str(value).lower())


def to_assets(doc: dict[str, Any]) -> list[CryptoAsset]:
    assets: list[CryptoAsset] = []
    for comp in doc.get("components") or []:
        if not isinstance(comp, dict):
            continue
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
            bom_ref=comp.get("bom_ref") or comp.get("bom-ref") or raw_name,
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
