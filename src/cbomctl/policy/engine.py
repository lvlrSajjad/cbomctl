"""Rule matching and cell verdicts.

Three invariants:

1. An unresolved purpose can never produce PASS. If we do not know what a key
   is for, we do not know whether a purpose-scoped rule bites.
2. A rule needing a fact the user did not declare produces INDETERMINATE, not a
   pass. "Informational" reads as "fine"; indeterminate does not.
3. `binding` decides FAIL versus WARN. A guideline that recommends cannot FAIL.
"""

from __future__ import annotations

from cbomctl.models import (
    Cell, CryptoAsset, Purpose, RuleRef, Verdict,
)
from cbomctl.policy.schema import Pack, Rule


def _selector_hit(values: list, actual) -> bool | None:
    """None when the selector is empty (no constraint)."""
    if not values:
        return None
    return actual in values


def rule_applies(rule: Rule, asset: CryptoAsset, *, system_category: str | None) -> tuple[bool, str | None]:
    """Return (applies, indeterminate_reason)."""
    a = rule.applies_to

    if a.purpose:
        if not asset.purpose.is_resolved:
            return False, (
                f"purpose is {asset.purpose.value}; this rule is scoped to "
                f"{', '.join(p.value for p in a.purpose)} and cannot be evaluated"
            )
        if asset.purpose not in a.purpose:
            return False, None

    if a.quantum_status and asset.quantum_status not in a.quantum_status:
        return False, None

    if a.construction and asset.construction not in a.construction:
        return False, None

    if a.exclude_algorithm:
        from cbomctl.normalize.identity import canonical_name

        excluded = {canonical_name(n) for n in a.exclude_algorithm}
        subject = canonical_name(asset.algorithm or asset.raw_name)
        if any(e in subject or subject in e for e in excluded):
            return False, None

    if a.algorithm:
        # Canonical substring, matching exclude_algorithm. Exact matching was
        # brittle: a rule naming "SLH-DSA" silently failed to reach an asset
        # called "SLH-DSA-SHA2-192s", because real names carry parameters.
        from cbomctl.normalize.identity import canonical_name

        wanted = {canonical_name(n) for n in a.algorithm}
        candidates = [canonical_name(asset.algorithm or ""),
                      canonical_name(asset.raw_name)]
        if not any(w and (w in c or c in w) for w in wanted for c in candidates if c):
            return False, None

    if a.parameter_set:
        from cbomctl.normalize.identity import canonical_name

        wanted = {canonical_name(x) for x in a.parameter_set}
        subject = canonical_name(
            f"{asset.algorithm or ''}{asset.raw_name}{asset.parameter_set or ''}"
            f"{asset.key_size or ''}")
        if not any(w in subject for w in wanted):
            return False, None

    if a.system_category:
        if system_category is None:
            return False, (
                f"rule is scoped to system categories "
                f"({', '.join(a.system_category)}) and none is declared; set "
                f"system_category in cbomctl.yaml"
            )
        if system_category not in a.system_category:
            return False, None

    if a.security_level:
        # Derived from key size, curve, or the CBOM's own
        # `classicalSecurityLevel`. When it cannot be derived we say so rather
        # than picking the stricter rule -- reporting RSA-3072 as deprecated in
        # 2030 because we could not compute its strength is exactly the error
        # this selector exists to avoid.
        if asset.security_strength is None:
            return False, (
                f"rule is scoped to security strength "
                f"{', '.join(a.security_level)} bits, which could not be "
                f"derived from this asset (no key size, curve or "
                f"classicalSecurityLevel)"
            )
        if str(asset.security_strength) not in a.security_level:
            return False, None

    return True, None


def _hybrid_satisfied(rule: Rule, asset: CryptoAsset) -> bool | None:
    """Whether the asset's construction matches the rule's hybrid stance.

    ``None`` when the rule takes no hybrid position for this purpose.
    """
    from cbomctl.models import Construction, HybridStance

    if rule.hybrid is None or rule.hybrid is HybridStance.SILENT:
        return None
    if rule.hybrid.favours_hybrid:
        return asset.construction is Construction.HYBRID
    if rule.hybrid.opposes_hybrid:
        return asset.construction is not Construction.HYBRID
    return None


def evaluate(
    pack: Pack,
    asset: CryptoAsset,
    *,
    system_category: str | None = None,
    include_acquisition_gate: bool = False,
    strict: bool = False,
) -> Cell:
    """Evaluate one asset against one pack."""
    from cbomctl.models import DeadlineState, RuleStatus

    hits: list[RuleRef] = []
    indeterminate_reasons: list[str] = []
    #: Rules skipped because the declared system category is outside this
    #: pack's scope. If that is the *only* reason nothing fired, the honest
    #: cell is "does not apply to you", not "passes".
    out_of_scope: list[str] = []
    #: A rule that applied and was satisfied. Distinguishes "this pack looked
    #: and was happy" from "this pack never reached you".
    satisfied: list[str] = []
    worst = Verdict.PASS

    for rule in pack.rules:
        if (rule.deadline_state is DeadlineState.ACQUISITION_GATE
                and not include_acquisition_gate):
            continue

        applies, reason = rule_applies(rule, asset, system_category=system_category)
        if reason:
            indeterminate_reasons.append(f"{rule.id}: {reason}")
            continue
        if not applies:
            if (rule.applies_to.system_category and system_category is not None
                    and system_category not in rule.applies_to.system_category):
                out_of_scope.append(rule.id)
            continue

        # A hybrid-stance rule only bites when the construction contradicts it.
        if _hybrid_satisfied(rule, asset) is True:
            satisfied.append(rule.id)
            continue

        verdict = rule.effective_verdict
        # Condition 2 of building on stubs: under --strict, a rule whose source
        # has not been verified cannot assert a verdict.
        if strict and rule.status is not RuleStatus.VERIFIED:
            verdict = Verdict.INDETERMINATE

        hits.append(RuleRef(
            rule_id=rule.id, jurisdiction=pack.id, binding=rule.binding,
            status=rule.status, source_url=rule.source_url,
            source_title=rule.source_title, is_draft=rule.is_draft,
            deadline=rule.deadline, deadline_state=rule.deadline_state,
            hybrid=rule.hybrid, rationale=rule.rationale,
            description=rule.description,
        ))
        if verdict.rank > worst.rank:
            worst = verdict

    # An unevaluable rule must not erase a verdict we *can* determine: a WARN
    # plus "one rule could not be evaluated" is more useful than INDET alone.
    # But INDETERMINATE must outrank PASS and INFO, or an unscoped
    # informational rule silently masks "I could not tell what this key is for".
    if indeterminate_reasons and worst.rank <= Verdict.INFO.rank:
        return Cell(verdict=Verdict.INDETERMINATE, rules=hits,
                    note="; ".join(indeterminate_reasons[:3]))

    if not hits and not indeterminate_reasons:
        # Invariant 1: never claim PASS for an asset whose purpose is unknown.
        if not asset.purpose.is_resolved:
            return Cell(
                verdict=Verdict.INDETERMINATE, rules=[],
                note=f"purpose is {asset.purpose.value}; no rule can be evaluated",
            )
        # "Does not apply to you" only holds if nothing in the pack actually
        # engaged. A rule that applied and was satisfied means this is a PASS.
        if out_of_scope and not satisfied and len(out_of_scope) == sum(
                1 for r in pack.rules if r.applies_to.system_category):
            return Cell(
                verdict=Verdict.NOT_APPLICABLE, rules=[],
                note=(f"every scoped rule in this pack targets a different "
                      f"system category; you declared {system_category!r}"),
            )
        return Cell(verdict=Verdict.PASS, rules=[])

    return Cell(verdict=worst, rules=hits,
                note="; ".join(indeterminate_reasons[:3]) or None)
