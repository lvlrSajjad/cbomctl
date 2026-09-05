"""Mosca scoring, and the urgency asymmetry it exists to encode."""

from __future__ import annotations

from datetime import date

import pytest

from cbomctl.models import CryptoAsset, Purpose, QuantumStatus, Risk, Unscored
from cbomctl.scoring.mosca import score

TODAY = date(2026, 9, 5)  # Z = 9 years to a 2035 CRQC assumption


def asset(purpose, status=QuantumStatus.BROKEN_BY_SHOR, name="X"):
    return CryptoAsset(bom_ref="r", raw_name=name, algorithm=name,
                       purpose=purpose, quantum_status=status)


def s(a, lifetime=25.0):
    return score(a, lifetime_years=lifetime, lifetime_source="test", today=TODAY)


class TestAsymmetry:
    def test_key_agreement_on_long_lived_data_is_critical(self):
        out = s(asset(Purpose.KEY_AGREEMENT))
        assert out.band == "critical"
        assert out.exposure_years == 19.0
        assert "harvest" in out.rationale

    def test_signature_with_same_numbers_is_not_critical(self):
        """The identical Mosca arithmetic must not produce the same band: a
        signature cannot be harvested."""
        kex = s(asset(Purpose.KEY_AGREEMENT))
        sig = s(asset(Purpose.SIGNATURE))
        assert kex.exposure_years == sig.exposure_years
        assert kex.band == "critical"
        assert sig.band == "medium"

    def test_short_lived_key_agreement_is_not_critical(self):
        assert s(asset(Purpose.KEY_AGREEMENT), lifetime=1.0).band == "medium"


class TestQuantumStatusGating:
    def test_grover_only_is_low_regardless_of_lifetime(self):
        """SHA-256 keeps ~128-bit quantum security. Reporting it as critical
        because the data lives 25 years is inflation."""
        out = s(asset(Purpose.HASH, QuantumStatus.WEAKENED_BY_GROVER, "SHA256"))
        assert out.band == "low"

    def test_pq_secure_scores_none(self):
        out = s(asset(Purpose.KEY_AGREEMENT, QuantumStatus.PQ_SECURE, "ML-KEM-1024"))
        assert out.band == "none"


class TestUnscorable:
    @pytest.mark.parametrize("p", [Purpose.UNKNOWN, Purpose.AMBIGUOUS])
    def test_unresolved_purpose_is_never_scored(self, p):
        out = s(asset(p))
        assert isinstance(out, Unscored)

    def test_ambiguous_reports_the_range_it_would_span(self):
        out = s(asset(Purpose.AMBIGUOUS))
        assert out.range_if_guessed == {"as_key_transport": "critical",
                                        "as_signature": "medium"}

    def test_unknown_does_not_invent_a_range(self):
        assert s(asset(Purpose.UNKNOWN)).range_if_guessed == {}

    def test_unscored_says_what_would_resolve_it(self):
        assert "cbomctl.yaml" in s(asset(Purpose.AMBIGUOUS)).would_resolve


class TestAssumptions:
    def test_crqc_year_moves_the_exposure(self):
        a = asset(Purpose.KEY_AGREEMENT)
        early = score(a, lifetime_years=25, lifetime_source="t",
                      crqc_year=2030, today=TODAY)
        late = score(a, lifetime_years=25, lifetime_source="t",
                     crqc_year=2040, today=TODAY)
        assert early.exposure_years > late.exposure_years

    def test_lifetime_source_is_recorded(self):
        assert s(asset(Purpose.KEY_AGREEMENT)).x_source == "test"
