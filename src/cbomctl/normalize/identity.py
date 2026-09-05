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
