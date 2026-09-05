"""End-to-end: matrix, conflicts, determinism, and the unverified banner."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest

from cbomctl.config import Config
from cbomctl.loader import read_assets
from cbomctl.models import Verdict
from cbomctl.policy.schema import load_pack
from cbomctl.report import json_out, markdown, matrix_text, sarif
from cbomctl.verdict.conflicts import detect
from cbomctl.verdict.matrix import build

FIXTURES = Path(__file__).parent / "fixtures"
TODAY = date(2026, 9, 5)
JURISDICTIONS = ["bsi-de", "anssi-fr", "asd-au", "cnsa-2.0"]


@pytest.fixture
def result():
    assets, _ = read_assets(FIXTURES / "conflict-hybrid.json")
    packs = [load_pack(j) for j in JURISDICTIONS]
    cfg = Config.model_validate({
        "system_category": "web-cloud",
        "assets": [{"match": {"location": "src/payments/**"},
                    "data_lifetime_years": 25}],
    })
    matrix = build(assets, packs, cfg, today=TODAY)
    return matrix, detect(matrix, packs), packs


class TestMatrix:
    def test_every_asset_gets_every_jurisdiction(self, result):
        matrix, _, _ = result
        for row in matrix.rows:
            assert set(row.cells) == set(JURISDICTIONS)

    def test_ambiguous_asset_is_never_passed_anywhere(self, result):
        matrix, _, _ = result
        row = next(r for r in matrix.rows if r.purpose == "ambiguous")
        assert all(c.verdict is not Verdict.PASS for c in row.cells.values())

    def test_config_lifetime_reaches_the_score(self, result):
        matrix, _, _ = result
        ecdh = next(r for r in matrix.rows if r.display == "ECDH")
        assert ecdh.risk.x_years == 25
        assert ecdh.risk.band == "critical"

    def test_hybrid_keeps_its_full_name(self, result):
        """`X25519MLKEM768` must not display as `ML-KEM` — the family token
        hides the classical half, which is the interesting part."""
        matrix, _, _ = result
        assert any(r.display == "X25519MLKEM768" for r in matrix.rows)

    def test_ordering_is_worst_first_and_stable(self, result):
        matrix, _, _ = result
        ranks = [r.worst.rank for r in matrix.rows]
        assert ranks == sorted(ranks, reverse=True)


class TestConflicts:
    def test_hybrid_construction_conflict_is_found(self, result):
        _, conflicts, _ = result
        c = next(c for c in conflicts if c.kind == "construction")
        assert {"bsi-de", "anssi-fr"} <= set(c.jurisdictions)
        assert "asd-au" in c.jurisdictions

    def test_construction_conflict_always_explains_the_trade(self, result):
        """Whether or not a satisfies-all target exists, the conflict must say
        so explicitly and name it as a business decision."""
        _, conflicts, _ = result
        found = [c for c in conflicts if c.kind == "construction"]
        assert found
        for c in found:
            assert "business decision" in c.cost_note
            if c.satisfies_all is None:
                assert "No single configuration" in c.cost_note

    def test_a_forbidding_jurisdiction_removes_the_satisfies_all_target(self):
        """cnsa-2.0 is modelled as not permitting hybrids outside interop
        exceptions. Paired with a pack that recommends them, no single
        construction works -- and inventing a compromise would be worse than
        useless."""
        assets, _ = read_assets(FIXTURES / "conflict-hybrid.json")
        packs = [load_pack("bsi-de"), load_pack("cnsa-2.0")]
        matrix = build(assets, packs, Config(system_category="web-cloud"),
                       today=TODAY)
        conflicts = detect(matrix, packs)
        construction = [c for c in conflicts if c.kind == "construction"]
        assert construction
        assert all(c.satisfies_all is None for c in construction)
        assert all("No single configuration" in c.cost_note for c in construction)

    def test_parameter_conflict_targets_the_stricter_set(self, result):
        _, conflicts, _ = result
        c = next((c for c in conflicts if c.kind == "parameter"), None)
        assert c is not None
        assert "1024" in c.satisfies_all

    def test_signature_conflict_exists_and_is_anssi_vs_asd(self, result):
        """The maturity axis: ANSSI recommends hybrid signatures, ASD does
        not. Neither position is about harvest risk."""
        _, conflicts, _ = result
        sig = next(c for c in conflicts
                   if c.kind == "construction" and "ML-DSA" in c.display)
        assert "anssi-fr" in sig.jurisdictions

    def test_conflict_ids_are_dense_and_referenced(self, result):
        matrix, conflicts, _ = result
        assert [c.id for c in conflicts] == [f"c{i}" for i in range(1, len(conflicts) + 1)]
        referenced = {i for r in matrix.rows for i in r.conflict_ids}
        assert referenced == {c.id for c in conflicts}


class TestUnverifiedIsUnmissable:
    """All seven shipped packs are now verified, so a synthetic fixture pack
    carries these tests. The machinery must not rot just because nothing
    currently triggers it -- the next unverified rule would ship silently."""

    @pytest.fixture
    def unverified(self):
        from cbomctl.policy.schema import Pack

        pack = Pack.from_file(FIXTURES / "packs" / "synthetic-unverified.yaml")
        assets, _ = read_assets(FIXTURES / "conflict-hybrid.json")
        matrix = build(assets, [pack], Config(), today=TODAY)
        return matrix, detect(matrix, [pack]), pack

    def test_no_shipped_pack_is_unverified(self, result):
        """Where verification has actually reached."""
        matrix, _, _ = result
        assert matrix.unverified_packs == []

    def test_matrix_reports_the_unverified_pack(self, unverified):
        matrix, _, _ = unverified
        assert matrix.unverified_packs == ["synthetic-unverified"]
        assert matrix.has_unverified

    def test_text_output_carries_the_banner(self, unverified):
        matrix, conflicts, _ = unverified
        out = matrix_text.render(matrix, conflicts)
        assert "UNVERIFIED POLICY PACK" in out
        assert "NOT FOR COMPLIANCE USE" in out

    def test_json_output_carries_a_machine_readable_warning(self, unverified):
        matrix, conflicts, _ = unverified
        doc = json.loads(json_out.render(matrix, conflicts))
        assert doc["policy_warning"]["level"] == "unverified"

    def test_markdown_output_carries_the_warning(self, unverified):
        matrix, conflicts, _ = unverified
        assert "UNVERIFIED POLICY PACK" in markdown.render(matrix, conflicts)

    def test_sarif_marks_every_unverified_rule(self, unverified):
        matrix, conflicts, _ = unverified
        doc = json.loads(sarif.render(matrix, conflicts))
        rules = doc["runs"][0]["tool"]["driver"]["rules"]
        policy = [r for r in rules if r["id"] != "cbomctl/jurisdiction-conflict"]
        assert policy
        for rule in policy:
            assert "[UNVERIFIED RULE]" in rule["fullDescription"]["text"]

    def test_draft_sources_are_announced(self, unverified):
        matrix, conflicts, _ = unverified
        assert matrix.draft_rules
        assert "DRAFT SOURCE" in matrix_text.render(matrix, conflicts)


class TestStrict:
    def test_strict_spares_verified_rules(self):
        """--strict blocks unverified rules from asserting a verdict. A rule
        read from its primary source is not affected."""
        assets, _ = read_assets(FIXTURES / "conflict-hybrid.json")
        matrix = build(assets, [load_pack("bsi-de")], Config(), strict=True, today=TODAY)
        assert any(c.verdict is Verdict.WARN
                   for r in matrix.rows for c in r.cells.values())

    def test_strict_downgrades_unverified_verdicts_to_indeterminate(self):
        from cbomctl.policy.schema import Pack

        pack = Pack.from_file(FIXTURES / "packs" / "synthetic-unverified.yaml")
        assets, _ = read_assets(FIXTURES / "conflict-hybrid.json")
        matrix = build(assets, [pack], Config(), strict=True, today=TODAY)
        assert all(c.verdict is not Verdict.FAIL
                   for r in matrix.rows for c in r.cells.values())
        assert matrix.exit_code == 3

    def test_strict_leaves_verified_packs_asserting(self):
        """--strict blocks unverified rules, not verified ones."""
        assets, _ = read_assets(FIXTURES / "conflict-hybrid.json")
        packs = [load_pack(j) for j in JURISDICTIONS]
        matrix = build(assets, packs, Config(), strict=True, today=TODAY)
        assert any(c.verdict in (Verdict.FAIL, Verdict.WARN)
                   for r in matrix.rows for c in r.cells.values())


class TestOutputs:
    def test_json_is_deterministic(self, result):
        matrix, conflicts, _ = result
        assert json_out.render(matrix, conflicts) == json_out.render(matrix, conflicts)

    def test_sarif_is_valid_2_1_0(self, result):
        matrix, conflicts, _ = result
        doc = json.loads(sarif.render(matrix, conflicts))
        assert doc["version"] == "2.1.0"
        assert doc["runs"][0]["tool"]["driver"]["name"] == "cbomctl"
        for res in doc["runs"][0]["results"]:
            assert res["locations"][0]["physicalLocation"]["artifactLocation"]["uri"]

    def test_exit_code_is_one_when_a_mandatory_rule_fails(self, result):
        matrix, _, _ = result
        assert matrix.exit_code == 1


class TestRealGeneratorOutput:
    def test_keycloak_cbom_parses_and_reports_its_unresolved_share(self):
        """Real CBOMkit output: a third of algorithm assets carry no usable
        purpose signal. If this ever drops to zero, the normalizer has started
        guessing."""
        assets, fmt = read_assets(FIXTURES / "cbomkit-keycloak.json")
        assert fmt == "cyclonedx"
        algorithms = [a for a in assets if a.asset_type == "algorithm"]
        assert len(algorithms) == 22
        unresolved = [a for a in algorithms if not a.purpose.is_resolved]
        assert 6 <= len(unresolved) <= 10

    def test_kafka_cbom_parses(self):
        assets, _ = read_assets(FIXTURES / "cbomkit-kafka.json")
        assert len(assets) == 11

    def test_spec_conformance_fixture_parses_all_asset_types(self):
        assets, _ = read_assets(FIXTURES / "spec-conformance-1.6.json")
        assert {a.asset_type for a in assets} == {
            "algorithm", "certificate", "protocol", "related-crypto-material"}


class TestSbomToolsAdapter:
    def test_adapter_is_detected_and_reads_crypto_properties(self):
        assets, fmt = read_assets(FIXTURES / "sbom-tools-view.json")
        assert fmt == "sbom-tools"
        ecdh = next(a for a in assets if a.raw_name == "ECDH")
        assert ecdh.purpose.value == "key-agreement"

    def test_adapter_preserves_ambiguity(self):
        assets, _ = read_assets(FIXTURES / "sbom-tools-view.json")
        rsa = next(a for a in assets if a.raw_name == "RSA-2048")
        assert rsa.purpose.value == "ambiguous"

    def test_absent_and_explicit_unknown_are_indistinguishable_here(self):
        """Documented loss: their parser collapses both to Unknown. No verdict
        changes, but the diagnostic is gone."""
        assets, _ = read_assets(FIXTURES / "sbom-tools-view.json")
        custom = next(a for a in assets if a.raw_name == "CustomKDF")
        assert custom.purpose.value == "unknown"


class TestConflictTargetsFitThePurpose:
    """A signature conflict must not offer a KEM as its resolution."""

    def test_signature_conflict_offers_signature_targets_only(self):
        assets, _ = read_assets(FIXTURES / "signatures.json")
        packs = [load_pack(p) for p in ("bsi-de", "anssi-fr", "asd-au", "cnsa-2.0")]
        matrix = build(assets, packs, Config(), today=TODAY)
        for c in detect(matrix, packs):
            if c.kind != "parameter" or not c.satisfies_all:
                continue
            row = next(r for r in matrix.rows if r.bom_ref == c.bom_ref)
            if row.purpose == "signature":
                assert "KEM" not in c.satisfies_all.upper(), c.satisfies_all
