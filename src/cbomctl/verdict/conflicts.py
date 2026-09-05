"""Conflict detection — the thing that is actually ours.

A conflict is not merely two different verdicts. Two jurisdictions can both say
FAIL for unrelated reasons and be perfectly compatible: fix the asset and both
clear. A conflict exists when satisfying one authority moves you *away* from
satisfying another.

Four kinds:

``construction``  one recommends or requires hybrid where another recommends
                  against it (BSI/ANSSI vs ASD)
``parameter``     both accept the algorithm, at different strengths
                  (ML-KEM-768 vs CNSA 2.0's ML-KEM-1024)
``deadline``      same requirement, dates far enough apart that the earlier
                  effectively governs
``scope``         one pack binds this asset and another demonstrably does not
"""

from __future__ import annotations

from cbomctl.models import Conflict, Construction, HybridStance, Verdict
from cbomctl.policy.schema import Pack
from cbomctl.verdict.matrix import Matrix, Row

#: Below this gap, two deadlines are the same plan.
DEADLINE_CONFLICT_YEARS = 3


def _hybrid_stances(row: Row, packs: dict[str, Pack]) -> dict[str, HybridStance]:
    """Each jurisdiction's hybrid stance *for this asset's purpose*."""
    out: dict[str, HybridStance] = {}
    for jid, cell in row.cells.items():
        pack = packs.get(jid)
        if pack is None:
            continue
        for rule in pack.rules:
            if rule.hybrid is None or rule.hybrid is HybridStance.SILENT:
                continue
            scoped = rule.applies_to.purpose
            if scoped and row.purpose not in [p.value for p in scoped]:
                continue
            out[jid] = rule.hybrid
            break
    return out


def _construction_conflict(row: Row, packs: dict[str, Pack], cid: str) -> Conflict | None:
    stances = _hybrid_stances(row, packs)
    pro = sorted(j for j, st in stances.items() if st.favours_hybrid)
    anti = sorted(j for j, st in stances.items() if st.opposes_hybrid)
    if not (pro and anti):
        return None

    required = any(stances[j] is HybridStance.REQUIRED for j in pro)
    # Do not lump "discourages" in with "forbids" -- the gradient is the point,
    # and it is the difference between a costly compromise and no compromise.
    forbidding = sorted(j for j in anti if not stances[j].permits_hybrid)
    discouraging = [j for j in anti if j not in forbidding]

    if forbidding:
        # A jurisdiction that does not permit hybrids at all cannot be
        # reconciled with one that recommends them. Saying so is the honest
        # output; inventing a compromise here would be worse than useless.
        satisfies = None
        also = ""
        if discouraging:
            also = (f" {', '.join(discouraging)} would permit a hybrid but "
                    f"recommends against it, so even dropping "
                    f"{', '.join(forbidding)} leaves a documented cost.")
        cost = (f"{', '.join(forbidding)} does not permit a hybrid construction "
                f"outside named interoperability exceptions, while "
                f"{', '.join(pro)} "
                f"{'require' if required else 'recommend'} one. **No single "
                f"configuration satisfies all selected jurisdictions.** You "
                f"will need different builds, or to drop a jurisdiction from "
                f"scope.{also} This is a business decision, not a technical "
                f"one.")
    else:
        # Discouraged-but-permitted: hybrid clears everyone, at a cost.
        satisfies = "hybrid (classical + PQC)"
        cost = (f"Hybrid is not recommended by {', '.join(anti)}, but is "
                f"permitted there and "
                f"{'required' if required else 'recommended'} by "
                f"{', '.join(pro)}. No construction is preferred by all; hybrid "
                f"is the only one compliant with all. This is a business "
                f"decision.")

    opposed = []
    if discouraging:
        opposed.append(f"{', '.join(discouraging)} recommend against it")
    if forbidding:
        opposed.append(f"{', '.join(forbidding)} does not permit one outside "
                       f"named interoperability exceptions")

    return Conflict(
        id=cid, kind="construction", bom_ref=row.bom_ref, display=row.display,
        summary=(f"{', '.join(pro)} "
                 f"{'require' if required else 'recommend'} a hybrid "
                 f"construction for {row.purpose}; "
                 + "; ".join(opposed) + "."),
        jurisdictions=sorted(stances),
        satisfies_all=satisfies, cost_note=cost,
    )


def _parameter_conflict(row: Row, packs: dict[str, Pack], cid: str) -> Conflict | None:
    """One jurisdiction rejects a parameter set the others accept."""
    from cbomctl.models import Rationale

    rejecting: dict[str, str] = {}
    for jid, cell in row.cells.items():
        for ref in cell.rules:
            if ref.rationale is Rationale.KEY_LENGTH:
                rejecting[jid] = ref.rule_id
    accepting = [j for j, c in row.cells.items()
                 if j not in rejecting and c.verdict in (Verdict.PASS, Verdict.WARN)]
    if not rejecting or not accepting:
        return None

    # Collect whatever the stricter jurisdictions actually name as a target.
    # Looking only at `kem` was a bug: ASD's SHA-256 -> SHA-384 and AES-128 ->
    # AES-256 rules carry `hash` and `symmetric` targets, so the conflict
    # claimed a stricter set existed while naming none.
    targets: set[str] = set()
    for jid, rule_id in rejecting.items():
        pack = packs.get(jid)
        if not pack:
            continue
        for r in pack.rules:
            if r.id != rule_id or r.migration_target is None:
                continue
            mt = r.migration_target
            targets.update(x for x in (mt.kem, mt.signature, mt.symmetric, mt.hash) if x)

    if targets:
        satisfies = " / ".join(sorted(targets))
        cost = ("The stricter parameter set satisfies every selected "
                "jurisdiction, at a performance cost the others do not "
                "require.")
    else:
        satisfies = None
        cost = (f"{', '.join(sorted(rejecting))} requires a stronger parameter "
                f"set but names no replacement in the rules we hold, so **no "
                f"single configuration is known to satisfy all selected "
                f"jurisdictions.** Read the source for its required strength "
                f"before acting on this.")

    return Conflict(
        id=cid, kind="parameter", bom_ref=row.bom_ref, display=row.display,
        summary=(f"{', '.join(sorted(rejecting))} require a higher parameter "
                 f"set than {', '.join(sorted(accepting))} accept."),
        jurisdictions=sorted(set(rejecting) | set(accepting)),
        satisfies_all=satisfies,
        cost_note=cost,
    )


def _deadline_conflict(row: Row, cid: str) -> Conflict | None:
    dated = {j: c.governing_deadline for j, c in row.cells.items() if c.governing_deadline}
    if len(dated) < 2:
        return None
    earliest_j, earliest = min(dated.items(), key=lambda kv: kv[1])
    latest_j, latest = max(dated.items(), key=lambda kv: kv[1])
    if (latest - earliest).days < DEADLINE_CONFLICT_YEARS * 365:
        return None
    return Conflict(
        id=cid, kind="deadline", bom_ref=row.bom_ref, display=row.display,
        summary=(f"{earliest_j} requires this by {earliest.isoformat()}; "
                 f"{latest_j} allows until {latest.isoformat()}."),
        jurisdictions=sorted(dated),
        satisfies_all=f"meet the earlier date ({earliest.isoformat()})",
        cost_note=(f"{earliest_j} governs in practice — the later deadline "
                   f"provides no relief if you are bound by both."),
    )


def detect(matrix: Matrix, packs: list[Pack]) -> list[Conflict]:
    by_id = {p.id: p for p in packs}
    conflicts: list[Conflict] = []
    n = 0
    for row in matrix.rows:
        if len(row.cells) < 2:
            continue
        for builder in (
            lambda r, c: _construction_conflict(r, by_id, c),
            lambda r, c: _parameter_conflict(r, by_id, c),
            lambda r, c: _deadline_conflict(r, c),
        ):
            n += 1
            found = builder(row, f"c{n}")
            if found:
                conflicts.append(found)
                row.conflict_ids.append(found.id)
    # Renumber densely so ids are stable and readable.
    for i, c in enumerate(conflicts, 1):
        old, c.id = c.id, f"c{i}"
        for row in matrix.rows:
            row.conflict_ids = [c.id if x == old else x for x in row.conflict_ids]
    return conflicts
