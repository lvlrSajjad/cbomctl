"""Purpose resolution — the precedence ladder from DESIGN §5.

Grounded in real generator output, not in the schema. In CBOMkit's published
Keycloak CBOM, of 22 algorithm components: 6 carry no ``cryptoFunctions`` at
all; ``keygen`` appears 12 times and says nothing about what a key is *for*;
``AES`` and ``HMACSHA2`` are tagged ``primitive: other``; and five EC keys that
are ECDSA/ECDH in that codebase are tagged ``primitive: pke``.

So the two obvious implementations are both wrong. Trusting ``primitive``
reports five Keycloak EC keys as harvest-now-decrypt-later exposures they are
not. Trusting ``cryptoFunctions`` because it is present resolves most assets
from a value that carries no purpose information.

The ladder below takes the first signal that *decides*, keeps the ones that
disagree, and returns AMBIGUOUS or UNKNOWN rather than guessing.
"""

from __future__ import annotations

from cbomctl.models import Purpose, PurposeConflict, Signal
from cbomctl.normalize import oids

#: ``cryptoFunctions`` values that carry purpose information.
FUNCTION_PURPOSE: dict[str, Purpose] = {
    "encrypt": Purpose.ENCRYPTION,
    "decrypt": Purpose.ENCRYPTION,
    "sign": Purpose.SIGNATURE,
    "verify": Purpose.SIGNATURE,
    "encapsulate": Purpose.KEY_AGREEMENT,
    "decapsulate": Purpose.KEY_AGREEMENT,
    "digest": Purpose.HASH,
    "tag": Purpose.MAC,
    "keyderive": Purpose.KDF,
}

#: Present in the data, carries no purpose. ``keygen`` is the most common value
#: in real output and the least informative one.
NEUTRAL_FUNCTIONS = {"keygen", "other", "unknown", "generate"}

PRIMITIVE_PURPOSE: dict[str, Purpose] = {
    "key-agree": Purpose.KEY_AGREEMENT,
    "kem": Purpose.KEY_AGREEMENT,
    "block-cipher": Purpose.ENCRYPTION,
    "stream-cipher": Purpose.ENCRYPTION,
    "ae": Purpose.ENCRYPTION,
    "key-wrap": Purpose.ENCRYPTION,  # 1.7 only
    "signature": Purpose.SIGNATURE,
    "hash": Purpose.HASH,
    "xof": Purpose.HASH,
    "mac": Purpose.MAC,
    "kdf": Purpose.KDF,
    "drbg": Purpose.RNG,
    # `pke` is genuinely dual-use: RSA encrypts and signs with the same key
    # material, and CBOMkit applies it to EC keys. It cannot decide.
    "pke": Purpose.AMBIGUOUS,
}

#: Names unambiguous by construction. A name may establish identity; it decides
#: purpose only for these.
NAME_PURPOSE: dict[str, Purpose] = {
    "ECDH": Purpose.KEY_AGREEMENT,
    "ECDHE": Purpose.KEY_AGREEMENT,
    "DH": Purpose.KEY_AGREEMENT,
    "DHE": Purpose.KEY_AGREEMENT,
    "X25519": Purpose.KEY_AGREEMENT,
    "X448": Purpose.KEY_AGREEMENT,
    "ML-KEM": Purpose.KEY_AGREEMENT,
    "KYBER": Purpose.KEY_AGREEMENT,
    "FRODOKEM": Purpose.KEY_AGREEMENT,
    "RSASSA-PSS": Purpose.SIGNATURE,
    "ECDSA": Purpose.SIGNATURE,
    "ED25519": Purpose.SIGNATURE,
    "ED448": Purpose.SIGNATURE,
    "EDDSA": Purpose.SIGNATURE,
    "DSA": Purpose.SIGNATURE,
    "ML-DSA": Purpose.SIGNATURE,
    "SLH-DSA": Purpose.SIGNATURE,
    "DILITHIUM": Purpose.SIGNATURE,
    "SPHINCS": Purpose.SIGNATURE,
    "FALCON": Purpose.SIGNATURE,
    "HMAC": Purpose.MAC,
}


#: What each algorithm family is actually capable of.
#:
#: This exists because a higher-precedence signal can be *wrong* in a way the
#: ladder alone cannot catch. CBOMkit's Keycloak CBOM tags ``AES`` with
#: ``cryptoFunctions: ["decapsulate"]``. Taken at face value that resolves a
#: block cipher to key agreement — confidently, and with a
#: harvest-now-decrypt-later weighting attached. A symmetric cipher cannot
#: perform key agreement, so the correct output is AMBIGUOUS with the
#: disagreement recorded, not a wrong answer delivered with certainty.
#:
#: Families whose purpose genuinely is dual-use (RSA, bare EC) are absent and
#: therefore unconstrained.
PLAUSIBLE_PURPOSES: dict[str, frozenset[Purpose]] = {
    "AES": frozenset({Purpose.ENCRYPTION}),
    "CHACHA20": frozenset({Purpose.ENCRYPTION}),
    "CAMELLIA": frozenset({Purpose.ENCRYPTION}),
    "ARIA": frozenset({Purpose.ENCRYPTION}),
    "3DES": frozenset({Purpose.ENCRYPTION}),
    "DES": frozenset({Purpose.ENCRYPTION}),
    "SHA1": frozenset({Purpose.HASH}),
    "SHA224": frozenset({Purpose.HASH}),
    "SHA256": frozenset({Purpose.HASH}),
    "SHA384": frozenset({Purpose.HASH}),
    "SHA512": frozenset({Purpose.HASH}),
    "SHA3": frozenset({Purpose.HASH}),
    "MD5": frozenset({Purpose.HASH}),
    "HMAC": frozenset({Purpose.MAC}),
    "ECDH": frozenset({Purpose.KEY_AGREEMENT}),
    "ECDHE": frozenset({Purpose.KEY_AGREEMENT}),
    "DH": frozenset({Purpose.KEY_AGREEMENT}),
    "DHE": frozenset({Purpose.KEY_AGREEMENT}),
    "X25519": frozenset({Purpose.KEY_AGREEMENT}),
    "X448": frozenset({Purpose.KEY_AGREEMENT}),
    "ML-KEM": frozenset({Purpose.KEY_AGREEMENT}),
    "KYBER": frozenset({Purpose.KEY_AGREEMENT}),
    "FRODOKEM": frozenset({Purpose.KEY_AGREEMENT}),
    "ECDSA": frozenset({Purpose.SIGNATURE}),
    "ED25519": frozenset({Purpose.SIGNATURE}),
    "ED448": frozenset({Purpose.SIGNATURE}),
    "EDDSA": frozenset({Purpose.SIGNATURE}),
    "DSA": frozenset({Purpose.SIGNATURE}),
    "ML-DSA": frozenset({Purpose.SIGNATURE}),
    "SLH-DSA": frozenset({Purpose.SIGNATURE}),
    "DILITHIUM": frozenset({Purpose.SIGNATURE}),
    "SPHINCS": frozenset({Purpose.SIGNATURE}),
    "FALCON": frozenset({Purpose.SIGNATURE}),
    "RSASSA-PSS": frozenset({Purpose.SIGNATURE}),
}


def implausible_for(raw_name: str, purpose: Purpose) -> str | None:
    """Return a reason string when *purpose* is impossible for this algorithm."""
    if not purpose.is_resolved:
        return None
    from cbomctl.normalize.identity import family

    fam = family(raw_name)
    allowed = PLAUSIBLE_PURPOSES.get(fam)
    if allowed is None or purpose in allowed:
        return None
    return (f"{fam} cannot perform {purpose.value} "
            f"(expected {' or '.join(sorted(p.value for p in allowed))})")


class Resolution:
    __slots__ = ("purpose", "signal", "conflicts")

    def __init__(self, purpose: Purpose, signal: Signal,
                 conflicts: list[PurposeConflict] | None = None) -> None:
        self.purpose = purpose
        self.signal = signal
        self.conflicts = conflicts or []


def _from_functions(functions: list[str] | None) -> tuple[Purpose | None, list[Purpose]]:
    """Return a decision plus every distinct purpose seen.

    Neutral values are skipped entirely: they neither decide nor block a
    lower-precedence signal from deciding.
    """
    if not functions:
        return None, []
    seen: list[Purpose] = []
    for f in functions:
        key = (f or "").strip().lower()
        if key in NEUTRAL_FUNCTIONS:
            continue
        p = FUNCTION_PURPOSE.get(key)
        if p and p not in seen:
            seen.append(p)
    if not seen:
        return None, []
    if len(seen) > 1:
        return Purpose.AMBIGUOUS, seen
    return seen[0], seen


def _from_name(raw_name: str) -> Purpose | None:
    from cbomctl.normalize.identity import canonical_name

    n = canonical_name(raw_name)
    for key in sorted(NAME_PURPOSE, key=len, reverse=True):
        if canonical_name(key) in n:
            return NAME_PURPOSE[key]
    return None


def resolve(
    *,
    raw_name: str,
    crypto_functions: list[str] | None = None,
    primitive: str | None = None,
    oid: str | None = None,
) -> Resolution:
    """Resolve purpose, recording which signal decided and what disagreed."""
    conflicts: list[PurposeConflict] = []

    def decide(purpose: Purpose, signal: Signal) -> Resolution:
        """Accept a decision unless the algorithm cannot possibly do it."""
        reason = implausible_for(raw_name, purpose)
        if reason:
            conflicts.append(PurposeConflict(
                signal=signal, suggested=purpose,
                note=f"{signal.value} suggests {purpose.value}, but {reason}; "
                     "reported as ambiguous rather than resolved incorrectly",
            ))
            return Resolution(Purpose.AMBIGUOUS, signal, conflicts)
        return Resolution(purpose, signal, conflicts)

    oid_entry = oids.lookup(oid)
    oid_purpose = oid_entry.purpose if oid_entry else None
    prim_purpose = PRIMITIVE_PURPOSE.get((primitive or "").strip().lower())
    name_purpose = _from_name(raw_name)

    def note_conflicts(chosen: Purpose, chosen_signal: Signal) -> None:
        for sig, other in (
            (Signal.PRIMITIVE, prim_purpose),
            (Signal.OID, oid_purpose),
            (Signal.NAME, name_purpose),
        ):
            if sig is chosen_signal or other is None:
                continue
            if other is not chosen and other is not Purpose.AMBIGUOUS:
                conflicts.append(PurposeConflict(
                    signal=sig, suggested=other,
                    note=f"{sig.value} suggests {other.value}, "
                         f"{chosen_signal.value} decided {chosen.value}",
                ))

    # 1 — cryptoFunctions, purpose-bearing values only.
    decided, seen = _from_functions(crypto_functions)
    if decided is Purpose.AMBIGUOUS:
        for p in seen:
            conflicts.append(PurposeConflict(
                signal=Signal.CRYPTO_FUNCTIONS, suggested=p,
                note="multiple purpose-bearing cryptoFunctions present",
            ))
        return Resolution(Purpose.AMBIGUOUS, Signal.CRYPTO_FUNCTIONS, conflicts)
    if decided is not None:
        note_conflicts(decided, Signal.CRYPTO_FUNCTIONS)
        return decide(decided, Signal.CRYPTO_FUNCTIONS)

    # 2 — primitive. `pke` reaches here as AMBIGUOUS and gets one chance to be
    # rescued by a purpose-specific OID, which is a stronger signal about use.
    if prim_purpose is Purpose.AMBIGUOUS:
        if oid_purpose is not None:
            note_conflicts(oid_purpose, Signal.OID)
            return decide(oid_purpose, Signal.OID)
        if name_purpose is not None:
            note_conflicts(name_purpose, Signal.NAME)
            return decide(name_purpose, Signal.NAME)
        return Resolution(Purpose.AMBIGUOUS, Signal.PRIMITIVE, conflicts)
    if prim_purpose is not None:
        note_conflicts(prim_purpose, Signal.PRIMITIVE)
        return decide(prim_purpose, Signal.PRIMITIVE)

    # 3 — OID, but only when it names a use rather than an algorithm.
    if oid_purpose is not None:
        note_conflicts(oid_purpose, Signal.OID)
        return decide(oid_purpose, Signal.OID)

    # 4 — name, last resort.
    if name_purpose is not None:
        return decide(name_purpose, Signal.NAME)

    return Resolution(Purpose.UNKNOWN, Signal.NONE, conflicts)
