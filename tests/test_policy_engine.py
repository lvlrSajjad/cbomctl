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
            assert "§" in rule.source_title, (
                f"{pid}/{rule.id} cites no section — 'verified' means a specific "
                f"passage was read, not that the document was skimmed")

    def test_verification_progress_is_pinned(self):
        """Verification proceeds pack by pack and rule by rule. This pins where
        it has reached, so a pack cannot quietly claim verification it has not
        earned -- and so the reverse (a rule regressing) is also caught."""
        fully = {p for p in ALL_PACKS if load_pack(p).is_verified}
        assert fully == {"bsi-de", "us-eo14412", "nist-ir8547"}

        partial = {p: (len(load_pack(p).rules) - len(load_pack(p).unverified_rules),
                       len(load_pack(p).rules))
                   for p in ALL_PACKS}
        assert partial["anssi-fr"] == (5, 6)   # 2027 cert date not in the source
        assert partial["asd-au"] == (0, 3)
        assert partial["cnsa-2.0"] == (0, 5)
        assert partial["eu-roadmap"] == (0, 3)

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
        """A Commission Recommendation is non-binding (TFEU Art. 288)."""
        for rule in load_pack("eu-roadmap").rules:
            assert rule.effective_verdict is not Verdict.FAIL


class TestNeverSilentlyPass:
    @pytest.mark.parametrize("p", [Purpose.UNKNOWN, Purpose.AMBIGUOUS])
    @pytest.mark.parametrize("pid", ALL_PACKS)
    def test_unresolved_purpose_never_passes(self, p, pid):
        cell = evaluate(load_pack(pid), asset(purpose=p))
        assert cell.verdict is not Verdict.PASS

    def test_undeclared_cnsa_category_is_indeterminate(self):
        cell = evaluate(load_pack("cnsa-2.0"),
                        asset(purpose=Purpose.HASH, status=QuantumStatus.WEAKENED_BY_GROVER,
                              name="SHA256"),
                        system_category=None)
        assert cell.verdict is Verdict.INDETERMINATE
        assert "system_category" in (cell.note or "")

    def test_strict_turns_unverified_rules_indeterminate(self):
        """Second condition of building on stubs."""
        # Uses a pack that is still unverified. CNSA rules are scoped to
        # system categories, so declare one -- otherwise the cell would be
        # INDETERMINATE for a different reason and prove nothing.
        kw = {"system_category": "web-cloud"}
        plain = evaluate(load_pack("cnsa-2.0"), asset(), **kw)
        strict = evaluate(load_pack("cnsa-2.0"), asset(), strict=True, **kw)
        assert plain.verdict is Verdict.FAIL
        assert strict.verdict is Verdict.INDETERMINATE

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
