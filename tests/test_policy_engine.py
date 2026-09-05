"""Pack loading, binding semantics, and the invariants around not-answering."""

from __future__ import annotations

import pytest

from cbomctl.models import (
    Binding, Construction, CryptoAsset, Purpose, QuantumStatus, RuleStatus, Verdict,
)
from cbomctl.policy.engine import evaluate
from cbomctl.policy.schema import available, load_pack

ALL_PACKS = available()


def asset(purpose=Purpose.KEY_AGREEMENT, construction=Construction.CLASSICAL,
          status=QuantumStatus.BROKEN_BY_SHOR, name="ECDH"):
    return CryptoAsset(bom_ref="r", raw_name=name, algorithm=name, purpose=purpose,
                       construction=construction, quantum_status=status)


class TestPacksAreHonest:
    def test_all_six_packs_load(self):
        assert set(ALL_PACKS) == {"anssi-fr", "asd-au", "bsi-de", "cnsa-2.0",
                                  "eu-roadmap", "nist-ir8547", "us-eo14412"}

    @pytest.mark.parametrize("pid", ALL_PACKS)
    def test_every_unverified_rule_states_its_open_question(self, pid):
        """An unverified rule must say what would settle it."""
        for rule in load_pack(pid).rules:
            if rule.status is RuleStatus.NEEDS_VERIFICATION:
                assert rule.open_question, f"{pid}/{rule.id} has no open question"

    @pytest.mark.parametrize("pid", ALL_PACKS)
    def test_every_verified_rule_names_its_reader_and_section(self, pid):
        """Verified means a person read the primary text. Prove it: a named
        verifier, a pinned edition, and a section in the source title."""
        for rule in load_pack(pid).rules:
            if rule.status is not RuleStatus.VERIFIED:
                continue
            assert rule.verified_by, f"{pid}/{rule.id} claims verified with no verifier"
            assert rule.source_edition, f"{pid}/{rule.id} has no pinned edition"
            import re as _re

            assert "§" in rule.source_title or _re.search(
                r"\bp{1,2}\.\s*\d", rule.source_title), (
                f"{pid}/{rule.id} cites neither a section nor a page — "
                f"'verified' means a specific passage was read, not that the "
                f"document was skimmed")

    def test_verification_progress_is_pinned(self):
        """Verification proceeds pack by pack and rule by rule. This pins where
        it has reached, so a pack cannot quietly claim verification it has not
        earned -- and so the reverse (a rule regressing) is also caught."""
        fully = {p for p in ALL_PACKS if load_pack(p).is_verified}
        assert fully == set(ALL_PACKS), "all seven packs are now verified"

        partial = {p: (len(load_pack(p).rules) - len(load_pack(p).unverified_rules),
                       len(load_pack(p).rules))
                   for p in ALL_PACKS}
        # The 2027 certification rule was removed rather than left unverified:
        # its date came only from press coverage.
        assert partial["anssi-fr"] == (5, 5)
        assert partial["asd-au"] == (6, 6)
        assert partial["cnsa-2.0"] == (9, 9)
        assert partial["eu-roadmap"] == (6, 6)

    @pytest.mark.parametrize("pid", ALL_PACKS)
    def test_every_pack_declares_who_it_binds(self, pid):
        assert load_pack(pid).applicability.strip()


class TestBindingDecidesSeverity:
    def test_bsi_recommends_and_therefore_cannot_fail(self):
        """TR-02102-1's operative verb is 'recommends'. Verified against the
        primary PDF, so this is not an assumption about its force."""
        pack = load_pack("bsi-de")
        assert all(r.binding is Binding.GUIDELINE_RECOMMENDATION for r in pack.rules)
        assert all(r.effective_verdict is not Verdict.FAIL for r in pack.rules)

    def test_a_recommendation_cannot_fail(self):
        """The review found our drafts overstating guidance as mandates. A
        guideline_recommendation is downgraded to WARN whatever the YAML says."""
        for rule in load_pack("bsi-de").rules:
            if rule.binding is Binding.GUIDELINE_RECOMMENDATION:
                assert rule.effective_verdict is not Verdict.FAIL

    def test_an_executive_order_can_fail(self):
        eo = load_pack("us-eo14412")
        assert any(r.effective_verdict is Verdict.FAIL for r in eo.rules)

    def test_eu_roadmap_never_fails(self):
        """The roadmap's language is "it is recommended"; a Commission
        Recommendation is non-binding on operators under TFEU Art. 288."""
        for rule in load_pack("eu-roadmap").rules:
            assert rule.effective_verdict is not Verdict.FAIL


class TestNeverSilentlyPass:
    @pytest.mark.parametrize("p", [Purpose.UNKNOWN, Purpose.AMBIGUOUS])
    @pytest.mark.parametrize("pid", ALL_PACKS)
    def test_unresolved_purpose_never_passes(self, p, pid):
        cell = evaluate(load_pack(pid), asset(purpose=p))
        assert cell.verdict is not Verdict.PASS

    def test_undeclared_system_category_is_indeterminate(self):
        """EO 14412 scopes every rule to HVAs and high impact systems, which is
        not derivable from a CBOM. With nothing declared there is nothing else
        to fall back on, so the cell is INDETERMINATE.

        (CNSA 2.0 carried category rules in the pre-release stub; the real FAQ
        v2.1 has none, so this mechanism now lives in the EO and EU packs.)"""
        cell = evaluate(load_pack("us-eo14412"), asset(), system_category=None)
        assert cell.verdict is Verdict.INDETERMINATE
        assert "system_category" in (cell.note or "")

    def test_undeclared_category_is_still_reported_beside_a_real_verdict(self):
        """The EU roadmap has both category-scoped and unscoped rules. The
        unscoped ones still produce a verdict, and the undeclared category is
        reported alongside rather than erasing it -- a WARN plus "one rule
        could not be evaluated" is more actionable than INDETERMINATE alone."""
        cell = evaluate(load_pack("eu-roadmap"), asset(), system_category=None)
        assert cell.verdict is Verdict.WARN
        assert "system_category" in (cell.note or "")

    def test_strict_turns_unverified_rules_indeterminate(self):
        """All seven shipped packs are verified, so this uses the synthetic
        fixture pack -- the mechanism must stay tested regardless."""
        from pathlib import Path

        from cbomctl.policy.schema import Pack

        pack = Pack.from_file(Path(__file__).parent / "fixtures" / "packs"
                              / "synthetic-unverified.yaml")
        assert evaluate(pack, asset()).verdict is Verdict.FAIL
        assert evaluate(pack, asset(), strict=True).verdict is Verdict.INDETERMINATE

    def test_acquisition_gate_is_off_by_default(self):
        ids = {r.rule_id for r in evaluate(load_pack("cnsa-2.0"), asset(),
                                           system_category="web-cloud").rules}
        assert "cnsa2-acquisition-gate-2027" not in ids
        ids_on = {r.rule_id for r in evaluate(load_pack("cnsa-2.0"), asset(),
                                              system_category="web-cloud",
                                              include_acquisition_gate=True).rules}
        assert "cnsa2-acquisition-gate-2027" in ids_on


class TestHybridIsPerPurpose:
    def test_anssi_recommends_hybrid_for_signatures_on_maturity_grounds(self):
        """The second axis: not a harvest argument, and it applies to
        signatures, which cannot be harvested at all."""
        from cbomctl.models import HybridStance, Rationale

        rule = next(r for r in load_pack("anssi-fr").rules
                    if r.applies_to.purpose == [Purpose.SIGNATURE])
        assert rule.hybrid is HybridStance.RECOMMENDED
        assert rule.rationale is Rationale.ALGORITHM_MATURITY

    def test_bsi_recommends_hybrid_signatures(self):
        """Verified: §5.3.4 recommends a quantum-safe signature scheme "only in
        combination with a classic signature scheme". So Europe splits from the
        anglophone agencies on signatures as well as key establishment."""
        from cbomctl.models import HybridStance, Rationale

        rule = next(r for r in load_pack("bsi-de").rules
                    if r.id == "bsi-hybrid-signatures")
        assert rule.hybrid is HybridStance.RECOMMENDED
        assert rule.rationale is Rationale.ALGORITHM_MATURITY

    def test_bsi_exempts_hash_based_signatures_from_hybrid(self):
        """§5.3.4 carve-out: hash-based schemes "can ... in principle also be
        used alone (i.e. not in hybrid form)". A widely-cited secondary summary
        says BSI wants hybrid for *all* PQC including hash-based; the primary
        text does not."""
        from cbomctl.models import Construction, QuantumStatus

        slh = asset(purpose=Purpose.SIGNATURE, construction=Construction.PURE_PQC,
                    status=QuantumStatus.PQ_SECURE, name="SLH-DSA-SHA2-192s")
        fired = {r.rule_id for r in evaluate(load_pack("bsi-de"), slh).rules}
        assert "bsi-hybrid-signatures" not in fired

    def test_bsi_still_wants_hybrid_for_lattice_signatures(self):
        """The carve-out is specific to hash-based schemes."""
        from cbomctl.models import Construction, QuantumStatus

        mldsa = asset(purpose=Purpose.SIGNATURE, construction=Construction.PURE_PQC,
                      status=QuantumStatus.PQ_SECURE, name="ML-DSA-65")
        fired = {r.rule_id for r in evaluate(load_pack("bsi-de"), mldsa).rules}
        assert "bsi-hybrid-signatures" in fired

    def test_hybrid_construction_satisfies_a_recommending_pack(self):
        cell = evaluate(load_pack("anssi-fr"),
                        asset(construction=Construction.HYBRID,
                              status=QuantumStatus.PQ_SECURE, name="X25519MLKEM768"))
        assert cell.verdict is Verdict.PASS

    def test_same_construction_warns_under_a_discouraging_pack(self):
        cell = evaluate(load_pack("asd-au"),
                        asset(construction=Construction.HYBRID,
                              status=QuantumStatus.PQ_SECURE, name="X25519MLKEM768"))
        assert cell.verdict is Verdict.WARN


class TestHybridGradient:
    """The hybrid axis is a three-step gradient, not a binary."""

    def test_three_distinct_stances_exist_across_packs(self):
        from cbomctl.models import HybridStance

        stances = {}
        for pid in ALL_PACKS:
            for rule in load_pack(pid).rules:
                if rule.hybrid and rule.hybrid is not HybridStance.SILENT:
                    stances.setdefault(rule.hybrid, set()).add(pid)
        assert HybridStance.RECOMMENDED in stances
        assert HybridStance.NOT_RECOMMENDED in stances
        assert HybridStance.NOT_PERMITTED_EXCEPT_INTEROP in stances

    def test_not_recommended_still_permits_hybrid(self):
        """ASD discourages without prohibiting, so a satisfies-all target can
        still exist at a documented cost."""
        from cbomctl.models import HybridStance

        assert HybridStance.NOT_RECOMMENDED.permits_hybrid
        assert HybridStance.NOT_RECOMMENDED.opposes_hybrid

    def test_not_permitted_forecloses_hybrid(self):
        from cbomctl.models import HybridStance

        assert not HybridStance.NOT_PERMITTED_EXCEPT_INTEROP.permits_hybrid
        assert HybridStance.NOT_PERMITTED_EXCEPT_INTEROP.opposes_hybrid


class TestEuropeanAlignment:
    """Verified from three primary sources: the European position on hybrid is
    consistent, and it is the opposite of ASD's."""

    def test_all_three_european_packs_recommend_hybrid(self):
        from cbomctl.models import HybridStance

        for pid in ("bsi-de", "anssi-fr", "eu-roadmap"):
            stances = {r.hybrid for r in load_pack(pid).rules if r.hybrid}
            assert HybridStance.RECOMMENDED in stances, pid

    def test_eu_roadmap_is_not_silent_on_hybrid(self):
        """The stub had this as `silent`. The primary text recommends hybrid
        explicitly, so silence was an assumption and it was wrong."""
        from cbomctl.models import HybridStance

        stances = {r.hybrid for r in load_pack("eu-roadmap").rules if r.hybrid}
        assert stances == {HybridStance.RECOMMENDED}


class TestScope:
    """A pack that demonstrably does not reach an asset says so."""

    def test_out_of_scope_pack_says_not_applicable_not_pass(self):
        """EO 14412 reaches federal HVAs and high impact systems. Run against a
        commercial web-cloud system it must not report PASS -- that reads as
        "you comply", when the truth is "this does not reach you"."""
        cell = evaluate(load_pack("us-eo14412"), asset(),
                        system_category="web-cloud")
        assert cell.verdict is Verdict.NOT_APPLICABLE
        assert "system category" in (cell.note or "")

    def test_in_scope_pack_still_evaluates(self):
        cell = evaluate(load_pack("us-eo14412"), asset(),
                        system_category="high-value-asset")
        assert cell.verdict is Verdict.FAIL

    def test_a_satisfied_rule_beats_out_of_scope(self):
        """N/A means "this pack never reached you". If a rule applied and was
        satisfied, the pack did reach you and was happy: that is PASS."""
        from cbomctl.models import Construction, QuantumStatus

        hybrid = asset(construction=Construction.HYBRID,
                       status=QuantumStatus.PQ_SECURE, name="X25519MLKEM768")
        cell = evaluate(load_pack("eu-roadmap"), hybrid, system_category="web-cloud")
        assert cell.verdict is Verdict.PASS

    def test_indeterminate_outranks_an_informational_rule(self):
        """An unscoped INFO rule must not mask "I cannot tell what this key is
        for". INDETERMINATE outranks PASS and INFO, but never FAIL or WARN."""
        cell = evaluate(load_pack("eu-roadmap"), asset(purpose=Purpose.AMBIGUOUS))
        assert cell.verdict is Verdict.INDETERMINATE

    def test_indeterminate_does_not_mask_a_real_warning(self):
        """The converse: a determinable WARN survives alongside an
        unevaluable rule, because it is more actionable than INDET alone."""
        cell = evaluate(load_pack("bsi-de"), asset())
        assert cell.verdict is Verdict.WARN
        assert cell.note  # the unevaluable rule is still reported

    def test_no_rule_has_an_empty_selector(self):
        """A rule with no selector fires on every asset and masks real
        findings. EO 14412's CISA-guidance provision was one; it now lives in
        the pack notes instead."""
        for pid in ALL_PACKS:
            for rule in load_pack(pid).rules:
                a = rule.applies_to
                assert any([a.purpose, a.quantum_status, a.construction,
                            a.algorithm, a.system_category, a.security_level]), (
                    f"{pid}/{rule.id} matches every asset")


class TestDraftSources:
    """A verified reading of a draft is still a draft."""

    def test_ir8547_rules_are_all_marked_draft(self):
        assert all(r.is_draft for r in load_pack("nist-ir8547").rules)

    def test_deprecated_and_disallowed_are_modelled_separately(self):
        """The most commonly misstated point in PQC compliance. NIST:
        deprecated means "may be used, but the user must accept some security
        risk"; disallowed means "no longer allowed"."""
        from cbomctl.models import DeadlineState

        states = {r.deadline_state for r in load_pack("nist-ir8547").rules}
        assert DeadlineState.DEPRECATED in states
        assert DeadlineState.DISALLOWED in states

    def test_2030_deprecation_only_reaches_112_bit_strength(self):
        """Table 2/4 deprecate 112-bit after 2030; >=128-bit is only
        disallowed after 2035. Coverage that says "RSA deprecated in 2030"
        without the strength qualifier is wrong."""
        pack = load_pack("nist-ir8547")
        for rule in pack.rules:
            if rule.deadline_state.value == "deprecated":
                assert rule.applies_to.security_level == ["112"]
            if rule.deadline_state.value == "disallowed":
                assert not rule.applies_to.security_level


class TestSourceDiscipline:
    @pytest.mark.parametrize("pid", ALL_PACKS)
    def test_every_source_url_is_a_primary_source(self, pid):
        from cbomctl.policy.schema import ALLOWED_SOURCE_HOSTS

        for rule in load_pack(pid).rules:
            assert any(h in rule.source_url for h in ALLOWED_SOURCE_HOSTS), rule.id


class TestCnsaContradictions:
    """CNSA 2.0 contradicts the European packs on two independent axes, both
    verified from the December 2024 FAQ v2.1."""

    def test_slh_dsa_is_not_approved_at_all(self):
        """BSI and ANSSI both exempt hash-based signatures from their hybrid
        recommendations -- i.e. approve them standalone. NSA does not approve
        SLH-DSA for any use in NSS."""
        from cbomctl.models import Construction, QuantumStatus

        slh = CryptoAsset(bom_ref="s", raw_name="SLH-DSA-SHA2-192s",
                          algorithm="SLH-DSA", purpose=Purpose.SIGNATURE,
                          construction=Construction.PURE_PQC,
                          quantum_status=QuantumStatus.PQ_SECURE)
        fired = {r.rule_id for r in evaluate(load_pack("cnsa-2.0"), slh).rules}
        assert "cnsa2-slh-dsa-not-approved" in fired

        for pid in ("bsi-de", "anssi-fr"):
            cell = evaluate(load_pack(pid), slh)
            assert cell.verdict is not Verdict.FAIL, pid

    def test_ml_kem_768_fails_cnsa_and_passes_europe(self):
        """"for all classification levels" -- there is no lower tier where 768
        becomes acceptable."""
        from cbomctl.models import Construction, QuantumStatus

        kem = asset(purpose=Purpose.KEY_AGREEMENT, construction=Construction.HYBRID,
                    status=QuantumStatus.PQ_SECURE, name="X25519MLKEM768")
        assert evaluate(load_pack("cnsa-2.0"), kem).verdict is Verdict.FAIL
        assert evaluate(load_pack("bsi-de"), kem).verdict is Verdict.PASS

    def test_ikev2_hybrid_is_the_named_exception(self):
        """The one place NSA affirmatively wants a hybrid. It must not inherit
        the general prohibition."""
        from cbomctl.models import Construction, HybridStance

        rule = next(r for r in load_pack("cnsa-2.0").rules
                    if r.id == "cnsa2-hybrid-ikev2-exception")
        assert rule.hybrid is HybridStance.REQUIRED

    def test_no_category_deadlines_survive_from_the_stub(self):
        """v2.1 has no per-product-category rows and never says 2033. Those
        came from the superseded 2022 chart."""
        pack = load_pack("cnsa-2.0")
        assert not any(r.applies_to.system_category for r in pack.rules)
        assert not any(r.deadline and r.deadline.year == 2033 for r in pack.rules)
        assert {r.deadline.year for r in pack.rules if r.deadline} == {2027, 2030, 2031}


class TestSecurityStrengthScoping:
    """The article's central claim, pinned: RSA-2048 and RSA-3072 have
    different fates under NIST IR 8547."""

    from pathlib import Path

    FIXTURE = Path(__file__).parent / "fixtures" / "rsa-strength-split.json"

    def _cells(self):
        from cbomctl.loader import read_assets

        assets, _ = read_assets(self.FIXTURE)
        pack = load_pack("nist-ir8547")
        return {a.display: evaluate(pack, a) for a in assets}

    @pytest.mark.parametrize("name,rule", [
        ("RSA-2048", "nist-112bit-key-establishment-deprecated-2030"),
        ("ECDSA-P224", "nist-112bit-signatures-deprecated-2030"),
    ])
    def test_112_bit_assets_are_deprecated_in_2030(self, name, rule):
        assert rule in {r.rule_id for r in self._cells()[name].rules}

    @pytest.mark.parametrize("name,rule", [
        ("RSA-3072", "nist-112bit-key-establishment-deprecated-2030"),
        ("ECDSA-P256", "nist-112bit-signatures-deprecated-2030"),
    ])
    def test_128_bit_assets_escape_the_2030_deprecation(self, name, rule):
        """The half of "RSA is deprecated in 2030" that is false -- and it is
        false for P-256 too, because IR 8547 scopes by strength rather than by
        algorithm."""
        assert rule not in {r.rule_id for r in self._cells()[name].rules}

    @pytest.mark.parametrize("name,rule", [
        ("RSA-2048", "nist-key-establishment-disallowed-2035"),
        ("RSA-3072", "nist-key-establishment-disallowed-2035"),
        ("ECDSA-P224", "nist-signatures-disallowed-2035"),
        ("ECDSA-P256", "nist-signatures-disallowed-2035"),
    ])
    def test_everything_is_disallowed_in_2035(self, name, rule):
        assert rule in {r.rule_id for r in self._cells()[name].rules}

    def test_names_stay_distinguishable(self):
        """Canonicalisation loses the parameter: both RSA sizes collapse to
        `RSA`, and both ECDSA curves resolve through one OID to
        `ECDSA-SHA256`. Display must not, or the distinction is invisible in
        every report."""
        assert set(self._cells()) == {"RSA-2048", "RSA-3072",
                                      "ECDSA-P224", "ECDSA-P256"}

    def test_the_right_cbom_field_is_read_for_strength(self):
        """`classicalSecurityLevel` is in bits. `nistQuantumSecurityLevel` is a
        category from 1 to 5. Reading the second as the first would score
        ML-KEM-768 as 3-bit security."""
        from cbomctl.loader import read_assets
        import json, tempfile, pathlib

        doc = {
            "bomFormat": "CycloneDX", "specVersion": "1.6", "version": 1,
            "components": [{
                "type": "cryptographic-asset", "bom-ref": "k", "name": "ML-KEM-768",
                "cryptoProperties": {"assetType": "algorithm", "algorithmProperties": {
                    "primitive": "kem", "nistQuantumSecurityLevel": 3,
                    "classicalSecurityLevel": 192}}}]}
        with tempfile.TemporaryDirectory() as d:
            f = pathlib.Path(d) / "c.json"
            f.write_text(json.dumps(doc))
            assets, _ = read_assets(f)
        assert assets[0].security_strength == 192

    def test_underivable_strength_is_indeterminate_not_stricter(self):
        """Erring strict is not safe: it competes for budget with real work."""
        from cbomctl.models import CryptoAsset, Purpose, QuantumStatus

        opaque = CryptoAsset(bom_ref="x", raw_name="ProprietaryKEX",
                             algorithm="ProprietaryKEX",
                             purpose=Purpose.KEY_AGREEMENT,
                             quantum_status=QuantumStatus.BROKEN_BY_SHOR)
        cell = evaluate(load_pack("nist-ir8547"), opaque)
        assert "could not be derived" in (cell.note or "")
