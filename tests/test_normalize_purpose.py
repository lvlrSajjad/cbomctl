"""Purpose resolution, including every path that must refuse to answer."""

from __future__ import annotations

import pytest

from cbomctl.models import Purpose, Signal
from cbomctl.normalize.purpose import resolve


def r(name, functions=None, primitive=None, oid=None):
    return resolve(raw_name=name, crypto_functions=functions,
                   primitive=primitive, oid=oid)


class TestNeutralFunctions:
    """`keygen` is the most common cryptoFunctions value in real output and
    carries no purpose information. It must never decide."""

    def test_keygen_alone_does_not_decide(self):
        assert r("Ed25519", ["keygen"], "signature").signal is Signal.PRIMITIVE

    def test_keygen_does_not_block_a_lower_signal(self):
        # No primitive at all: the OID must still get its chance.
        out = r("ECDH", ["keygen"], None, "1.3.132.1.12")
        assert out.purpose is Purpose.KEY_AGREEMENT
        assert out.signal is Signal.OID

    @pytest.mark.parametrize("fn", ["keygen", "other", "unknown"])
    def test_all_neutral_values_fall_through(self, fn):
        assert r("<opaque>", [fn]).purpose is Purpose.UNKNOWN


class TestAmbiguity:
    def test_pke_is_ambiguous_not_encryption(self):
        """`primitive: pke` cannot separate key transport from signature."""
        out = r("RSA-2048", ["keygen"], "pke", "1.2.840.113549.1.1.1")
        assert out.purpose is Purpose.AMBIGUOUS

    def test_rsa_encryption_oid_does_not_resolve_ambiguity(self):
        """`rsaEncryption` names the algorithm, not the use, despite the name.
        Every RSA key carries it, signing keys included."""
        assert r("RSA", None, "pke", "1.2.840.113549.1.1.1").purpose is Purpose.AMBIGUOUS

    def test_ec_public_key_oid_does_not_resolve_ambiguity(self):
        """id-ecPublicKey: EC keys both sign and agree."""
        assert r("EC-secp256r1", ["keygen"], "pke",
                 "1.2.840.10045.2.1").purpose is Purpose.AMBIGUOUS

    def test_purpose_specific_oid_does_rescue_pke(self):
        out = r("ECDH-thing", None, "pke", "1.3.132.1.12")
        assert out.purpose is Purpose.KEY_AGREEMENT
        assert out.signal is Signal.OID

    def test_conflicting_functions_are_ambiguous(self):
        out = r("DualUse", ["sign", "encrypt"])
        assert out.purpose is Purpose.AMBIGUOUS
        assert len(out.conflicts) == 2


class TestUnknown:
    def test_no_signal_at_all(self):
        out = r("RAW", ["keygen"], "other")
        assert out.purpose is Purpose.UNKNOWN
        assert out.signal is Signal.NONE

    def test_unknown_is_distinct_from_ambiguous(self):
        assert Purpose.UNKNOWN is not Purpose.AMBIGUOUS
        assert not Purpose.UNKNOWN.is_resolved
        assert not Purpose.AMBIGUOUS.is_resolved


class TestPlausibility:
    """A higher-precedence signal can be wrong in a way the ladder alone
    cannot catch. CBOMkit tags AES with `decapsulate`."""

    def test_aes_cannot_do_key_agreement(self):
        out = r("AES", ["decapsulate"], "other", "2.16.840.1.101.3.4.1")
        assert out.purpose is Purpose.AMBIGUOUS
        assert any("cannot perform" in c.note for c in out.conflicts)

    def test_plausible_decisions_are_untouched(self):
        assert r("SHA256", ["digest"], "hash").purpose is Purpose.HASH

    def test_dual_use_families_are_unconstrained(self):
        # RSA genuinely signs and encrypts; no plausibility veto applies.
        assert r("RSA-2048", ["sign"], None).purpose is Purpose.SIGNATURE


class TestHarvestability:
    @pytest.mark.parametrize("p,expected", [
        (Purpose.KEY_AGREEMENT, True), (Purpose.ENCRYPTION, True),
        (Purpose.SIGNATURE, False), (Purpose.HASH, False),
        (Purpose.UNKNOWN, False), (Purpose.AMBIGUOUS, False),
    ])
    def test_only_key_establishment_is_harvestable(self, p, expected):
        assert p.is_harvestable is expected
