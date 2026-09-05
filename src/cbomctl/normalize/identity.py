"""Canonical algorithm identity, construction, and quantum status.

Deliberately thin. Identity classification is well covered by other tools; what
this needs to do is produce a name a policy rule can match and decide whether a
construction is classical, pure PQC, or hybrid.
"""

from __future__ import annotations

import re

from cbomctl.models import Construction, QuantumStatus

PQ_KEM = {"ML-KEM", "KYBER", "FRODOKEM", "CLASSIC-MCELIECE", "HQC", "BIKE", "NTRU", "SNTRUP761"}
PQ_SIG = {"ML-DSA", "DILITHIUM", "SLH-DSA", "SPHINCS", "FALCON", "FN-DSA", "LMS", "XMSS", "HSS"}
SHOR_BROKEN = {"RSA", "DSA", "DH", "DHE", "ECDH", "ECDHE", "ECDSA", "EDDSA",
               "ED25519", "ED448", "X25519", "X448", "EC", "ELGAMAL", "ECIES", "ECMQV"}
GROVER_WEAKENED = {"AES", "CHACHA20", "CAMELLIA", "ARIA", "SHA1", "SHA224", "SHA256",
                   "SHA384", "SHA512", "SHA3", "SHAKE", "HMAC", "MD5", "3DES", "DES"}

_PARAM = re.compile(r"(\d{3,4})")
_CURVE = re.compile(r"(secp\d+[rk]\d|prime\d+v\d|brainpoolP\d+[rt]\d|Curve25519|Edwards25519|Edwards448|Curve448|P-\d+)", re.I)


def canonical_name(raw: str) -> str:
    """Uppercase, strip separators — for family matching, not display."""
    return re.sub(r"[^A-Z0-9]", "", raw.upper())


def family(raw: str) -> str:
    """Best-effort family token, e.g. ``AES128-CBC-PKCS5`` -> ``AES``."""
    n = canonical_name(raw)
    for f in sorted(PQ_KEM | PQ_SIG, key=len, reverse=True):
        if canonical_name(f) in n:
            return f
    for f in ("RSASSA-PSS", "ECDSA", "ECDHE", "ECDH", "EDDSA", "ED25519", "ED448",
              "X25519", "X448", "HMAC", "AES", "CHACHA20", "SHA3", "SHA512", "SHA384",
              "SHA256", "SHA224", "SHA1", "MD5", "3DES", "DES", "DSA", "DHE", "DH", "RSA", "EC"):
        if canonical_name(f) in n:
            return f
    return raw


def classify_quantum(raw: str) -> QuantumStatus:
    n = canonical_name(raw)
    for f in PQ_KEM | PQ_SIG:
        if canonical_name(f) in n:
            return QuantumStatus.PQ_SECURE
    for f in sorted(SHOR_BROKEN, key=len, reverse=True):
        if canonical_name(f) in n:
            return QuantumStatus.BROKEN_BY_SHOR
    for f in GROVER_WEAKENED:
        if canonical_name(f) in n:
            return QuantumStatus.WEAKENED_BY_GROVER
    return QuantumStatus.UNKNOWN


def classify_construction(raw: str, primitive: str | None = None) -> Construction:
    """Hybrid detection.

    A hybrid names both a classical and a PQ component (``X25519MLKEM768``,
    ``ecdh-nistp256-mlkem768``), or the CBOM says ``primitive: combiner``.
    """
    if primitive == "combiner":
        return Construction.HYBRID
    n = canonical_name(raw)
    has_pq = any(canonical_name(f) in n for f in PQ_KEM | PQ_SIG)
    has_classical = any(canonical_name(f) in n for f in
                        ("X25519", "X448", "ECDH", "ECDSA", "SECP", "NISTP", "RSA", "ED25519", "P256", "P384"))
    if has_pq and has_classical:
        return Construction.HYBRID
    if has_pq:
        return Construction.PURE_PQC
    if classify_quantum(raw) is QuantumStatus.BROKEN_BY_SHOR:
        return Construction.CLASSICAL
    return Construction.UNKNOWN


def parse_key_size(raw: str, parameter_set: str | None) -> int | None:
    if parameter_set and parameter_set.isdigit():
        return int(parameter_set)
    m = _PARAM.search(raw)
    return int(m.group(1)) if m else None


def parse_curve(raw: str, declared: str | None) -> str | None:
    if declared:
        return declared.split("/")[-1]
    m = _CURVE.search(raw)
    return m.group(1) if m else None


#: Classical security strength in bits, by RSA / finite-field modulus size.
#: Per NIST SP 800-57 Part 1 Rev. 5, Table 2.
_MODULUS_STRENGTH = {1024: 80, 2048: 112, 3072: 128, 4096: 152,
                     7680: 192, 15360: 256}

#: Curve -> classical security strength. Roughly half the field size.
_CURVE_STRENGTH = {
    "secp192r1": 96, "prime192v1": 96, "p-192": 96,
    "secp224r1": 112, "p-224": 112, "brainpoolp224r1": 112,
    "secp256r1": 128, "prime256v1": 128, "p-256": 128, "secp256k1": 128,
    "brainpoolp256r1": 128, "curve25519": 128, "edwards25519": 128,
    "x25519": 128, "ed25519": 128,
    "secp384r1": 192, "p-384": 192, "brainpoolp384r1": 192,
    "secp521r1": 256, "p-521": 256, "brainpoolp512r1": 256,
    "curve448": 224, "edwards448": 224, "x448": 224, "ed448": 224,
}

#: Symmetric and hash algorithms whose strength is not the raw digest length.
#: A hash's collision resistance is half its output, which is the figure NIST
#: transition tables are scoped to.
_NAMED_STRENGTH = {
    "AES128": 128, "AES192": 192, "AES256": 256,
    "SHA1": 80, "SHA224": 112, "SHA256": 128, "SHA384": 192, "SHA512": 256,
    "SHA3224": 112, "SHA3256": 128, "SHA3384": 192, "SHA3512": 256,
    "MD5": 0, "3DES": 112, "DES": 56,
}


def security_strength(
    raw_name: str,
    *,
    declared: int | None = None,
    key_size: int | None = None,
    curve: str | None = None,
) -> int | None:
    """Classical security strength in bits, or None when it cannot be derived.

    This is not cosmetic. NIST IR 8547 scopes its 2030 deprecation to 112-bit
    strength and leaves >=128-bit with only a 2035 disallowance, so RSA-2048 and
    RSA-3072 have genuinely different fates. A tool that cannot compute strength
    cannot tell them apart, and will report the stricter date for both.

    `classicalSecurityLevel` from the CBOM wins when present -- the generator
    may know something we cannot derive.
    """
    if declared:
        return int(declared)

    fam = family(raw_name)
    n = canonical_name(raw_name)

    if curve:
        hit = _CURVE_STRENGTH.get(curve.split("/")[-1].strip().lower())
        if hit:
            return hit
    for token, bits in _CURVE_STRENGTH.items():
        if canonical_name(token) and canonical_name(token) in n:
            return bits

    if fam in ("RSA", "DH", "DHE", "DSA") and key_size:
        if key_size in _MODULUS_STRENGTH:
            return _MODULUS_STRENGTH[key_size]
        # Between tabulated sizes, report the lower bracket rather than round up.
        lower = [k for k in sorted(_MODULUS_STRENGTH) if k <= key_size]
        return _MODULUS_STRENGTH[lower[-1]] if lower else None

    hit = _NAMED_STRENGTH.get(n)
    if hit is not None:
        return hit
    if fam in ("AES", "SHA1", "SHA224", "SHA256", "SHA384", "SHA512") and key_size:
        return _NAMED_STRENGTH.get(f"{fam}{key_size}", key_size)

    return None
