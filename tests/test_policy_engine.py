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
                                  "eu-roadmap", "us-eo14412"}

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

    def test_bsi_is_verified_and_the_rest_are_not(self):
        """Verification proceeds pack by pack; this pins where it has reached."""
        verified = {p for p in ALL_PACKS if load_pack(p).is_verified}
        assert verified == {"bsi-de"}

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
        # EO 14412 rules are scoped to system categories, so declare one:
        # otherwise the cell is already INDETERMINATE for a different reason.
        kw = {"system_category": "high-value-asset"}
        plain = evaluate(load_pack("us-eo14412"), asset(), **kw)
        strict = evaluate(load_pack("us-eo14412"), asset(), strict=True, **kw)
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


class TestSourceDiscipline:
    @pytest.mark.parametrize("pid", ALL_PACKS)
    def test_every_source_url_is_a_primary_source(self, pid):
        from cbomctl.policy.schema import ALLOWED_SOURCE_HOSTS

        for rule in load_pack(pid).rules:
            assert any(h in rule.source_url for h in ALLOWED_SOURCE_HOSTS), rule.id
