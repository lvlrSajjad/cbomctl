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
    def test_every_rule_is_unverified(self, pid):
        """Condition of building on stubs: nothing may claim to be verified."""
        pack = load_pack(pid)
        assert all(r.status is RuleStatus.NEEDS_VERIFICATION for r in pack.rules)

    @pytest.mark.parametrize("pid", ALL_PACKS)
    def test_every_unverified_rule_states_its_open_question(self, pid):
        for rule in load_pack(pid).rules:
            assert rule.open_question, f"{pid}/{rule.id} has no open question"

    @pytest.mark.parametrize("pid", ALL_PACKS)
    def test_every_pack_declares_who_it_binds(self, pid):
        assert load_pack(pid).applicability.strip()


class TestBindingDecidesSeverity:
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

    def test_bsi_signature_hybrid_stance_is_deliberately_unset(self):
        """Not yet read from TR-02102-1 2026-01, so not asserted."""
        rule = next(r for r in load_pack("bsi-de").rules
                    if r.applies_to.purpose == [Purpose.SIGNATURE])
        assert rule.hybrid is None

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
