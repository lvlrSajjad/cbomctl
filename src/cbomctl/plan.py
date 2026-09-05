"""Ordered migration plan.

Secondary to `verdict`: it consumes the matrix rather than re-deriving
anything. What to fix first, to which target, under whose deadline.
"""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field

from cbomctl.models import Conflict
from cbomctl.policy.schema import Pack
from cbomctl.verdict.matrix import Matrix


class Target(BaseModel):
    jurisdiction: str
    target: str
    construction: str | None = None
    deadline: date | None = None
    rule_id: str
    rule_status: str


class Step(BaseModel):
    order: int
    bom_ref: str
    display: str
    purpose: str
    band: str
    exposure_years: float | None
    governing_deadline: date | None
    locations: list[str] = Field(default_factory=list)
    targets: list[Target] = Field(default_factory=list)
    conflict_ids: list[str] = Field(default_factory=list)


def _targets(row, packs: dict[str, Pack]) -> list[Target]:
    out: list[Target] = []
    for jid, cell in sorted(row.cells.items()):
        pack = packs.get(jid)
        if pack is None:
            continue
        for ref in cell.rules:
            rule = next((r for r in pack.rules if r.id == ref.rule_id), None)
            if rule is None or rule.migration_target is None:
                continue
            mt = rule.migration_target
            named = mt.kem or mt.signature or mt.symmetric or mt.hash
            if not named:
                continue
            out.append(Target(
                jurisdiction=jid, target=named,
                construction=mt.construction.value if mt.construction else None,
                deadline=rule.deadline, rule_id=rule.id,
                rule_status=rule.status.value,
            ))
            break
    return out


def build(matrix: Matrix, conflicts: list[Conflict], packs: list[Pack]) -> list[Step]:
    by_id = {p.id: p for p in packs}
    steps: list[Step] = []
    order = 0
    for row in matrix.rows:
        targets = _targets(row, by_id)
        if not targets and not row.conflict_ids:
            continue
        order += 1
        steps.append(Step(
            order=order, bom_ref=row.bom_ref, display=row.display,
            purpose=row.purpose,
            band=row.risk.band if row.risk else "unscored",
            exposure_years=row.risk.exposure_years if row.risk else None,
            governing_deadline=row.governing_deadline,
            locations=row.locations, targets=targets,
            conflict_ids=row.conflict_ids,
        ))
    return steps


def render(matrix: Matrix, conflicts: list[Conflict], packs: list[Pack]) -> str:
    steps = build(matrix, conflicts, packs)
    out: list[str] = []
    if matrix.has_unverified:
        from cbomctl.report.matrix_text import _banner

        out += [_banner(matrix.unverified_packs), ""]

    if not steps:
        out.append("Nothing to migrate under the selected jurisdictions.")
        return "\n".join(out)

    for s in steps:
        head = f"{s.order}. {s.band.upper():<9} {s.display}  ({s.purpose})"
        if s.exposure_years is not None:
            head += f"  exposure {s.exposure_years}y"
        out.append(head)
        if s.governing_deadline:
            out.append(f"   governing deadline: {s.governing_deadline.isoformat()}")
        for loc in s.locations[:3]:
            out.append(f"   {loc}")
        for t in s.targets:
            cons = f" ({t.construction})" if t.construction else ""
            when = f" by {t.deadline.isoformat()}" if t.deadline else ""
            mark = "" if t.rule_status == "verified" else "  [unverified rule]"
            out.append(f"   → {t.jurisdiction:<12} {t.target}{cons}{when}{mark}")
        if s.conflict_ids:
            out.append(f"   ⚠ conflicts: {', '.join(s.conflict_ids)}")
        out.append("")

    if conflicts:
        out.append(f"CONFLICTS ({len(conflicts)})")
        for c in conflicts:
            out.append(f"  {c.id}  [{c.kind}]  {c.display} — {c.summary}")
            if c.satisfies_all:
                out.append(f"      satisfies all: {c.satisfies_all}")
    return "\n".join(out)
