"""OID table.

Two kinds of entry, and the distinction is the entire point of the file: an OID
that *identifies an algorithm* and an OID that *identifies a use*. Reading
purpose out of the former is the guess this tool refuses to make.

``1.2.840.113549.1.1.1`` is named ``rsaEncryption`` and tags every RSA key in
existence, signing keys included. It is ``purpose=None`` here.
"""

from __future__ import annotations

from dataclasses import dataclass

from cbomctl.models import Purpose


@dataclass(frozen=True)
class OidEntry:
    algorithm: str
    #: ``None`` when the OID names an algorithm rather than a use.
    purpose: Purpose | None = None
    curve: str | None = None


OIDS: dict[str, OidEntry] = {
    # ── purpose-specific: the OID names a use ────────────────────────────
    "1.3.132.1.12": OidEntry("ECDH", Purpose.KEY_AGREEMENT),
    "1.2.840.10046.2.1": OidEntry("DH", Purpose.KEY_AGREEMENT),
    "1.2.840.113549.1.1.10": OidEntry("RSASSA-PSS", Purpose.SIGNATURE),
    "1.2.840.113549.1.1.11": OidEntry("SHA256withRSA", Purpose.SIGNATURE),
    "1.2.840.113549.1.1.5": OidEntry("SHA1withRSA", Purpose.SIGNATURE),
    "1.2.840.10045.4.3.2": OidEntry("ECDSA-SHA256", Purpose.SIGNATURE),
    "1.2.840.10045.4.3.3": OidEntry("ECDSA-SHA384", Purpose.SIGNATURE),
    "1.2.840.10045.4.3.4": OidEntry("ECDSA-SHA512", Purpose.SIGNATURE),
    "1.2.840.10040.4.1": OidEntry("DSA", Purpose.SIGNATURE),
    "1.2.840.10040.4.3": OidEntry("DSA-SHA1", Purpose.SIGNATURE),
    "1.3.101.112": OidEntry("Ed25519", Purpose.SIGNATURE, curve="Edwards25519"),
    "1.3.101.113": OidEntry("Ed448", Purpose.SIGNATURE, curve="Edwards448"),
    "1.3.101.110": OidEntry("X25519", Purpose.KEY_AGREEMENT, curve="Curve25519"),
    "1.3.101.111": OidEntry("X448", Purpose.KEY_AGREEMENT, curve="Curve448"),
    "1.2.840.113549.1.1.8": OidEntry("MGF1"),
    "1.2.840.113549.2.9": OidEntry("HMAC-SHA256", Purpose.MAC),
    "1.2.840.113549.2.7": OidEntry("HMAC-SHA1", Purpose.MAC),
    # ── identity only: the OID names an algorithm, not a use ─────────────
    # rsaEncryption tags signing keys too. Never resolve purpose from it.
    "1.2.840.113549.1.1.1": OidEntry("RSA"),
    # id-ecPublicKey: EC keys both sign and agree.
    "1.2.840.10045.2.1": OidEntry("EC"),
    # ── hashes ───────────────────────────────────────────────────────────
    "1.3.14.3.2.26": OidEntry("SHA1", Purpose.HASH),
    "2.16.840.1.101.3.4.2.1": OidEntry("SHA256", Purpose.HASH),
    "2.16.840.1.101.3.4.2.2": OidEntry("SHA384", Purpose.HASH),
    "2.16.840.1.101.3.4.2.3": OidEntry("SHA512", Purpose.HASH),
    "1.2.840.113549.2.5": OidEntry("MD5", Purpose.HASH),
    # ── symmetric ────────────────────────────────────────────────────────
    "2.16.840.1.101.3.4.1": OidEntry("AES", Purpose.ENCRYPTION),
    "2.16.840.1.101.3.4.1.2": OidEntry("AES128-CBC", Purpose.ENCRYPTION),
    "2.16.840.1.101.3.4.1.6": OidEntry("AES128-GCM", Purpose.ENCRYPTION),
    "2.16.840.1.101.3.4.1.42": OidEntry("AES256-CBC", Purpose.ENCRYPTION),
    "2.16.840.1.101.3.4.1.46": OidEntry("AES256-GCM", Purpose.ENCRYPTION),
    # ── post-quantum (FIPS 203/204/205) ──────────────────────────────────
    "2.16.840.1.101.3.4.4.1": OidEntry("ML-KEM-512", Purpose.KEY_AGREEMENT),
    "2.16.840.1.101.3.4.4.2": OidEntry("ML-KEM-768", Purpose.KEY_AGREEMENT),
    "2.16.840.1.101.3.4.4.3": OidEntry("ML-KEM-1024", Purpose.KEY_AGREEMENT),
    "2.16.840.1.101.3.4.3.17": OidEntry("ML-DSA-44", Purpose.SIGNATURE),
    "2.16.840.1.101.3.4.3.18": OidEntry("ML-DSA-65", Purpose.SIGNATURE),
    "2.16.840.1.101.3.4.3.19": OidEntry("ML-DSA-87", Purpose.SIGNATURE),
}


def lookup(oid: str | None) -> OidEntry | None:
    return OIDS.get(oid.strip()) if oid else None
