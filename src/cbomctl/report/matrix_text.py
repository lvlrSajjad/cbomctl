"""Terminal matrix. The default output."""

from __future__ import annotations

from cbomctl.models import Conflict, Verdict
from cbomctl.verdict.matrix import Matrix

_BANNER_W = 74


def _banner(packs: list[str]) -> str:
    """Impossible to miss, and impossible to mistake for a real verdict."""
    joined = ", ".join(packs)
    if len(joined) > _BANNER_W - 20:
        joined = joined[: _BANNER_W - 21] + "…"
    lines = [
        "UNVERIFIED POLICY PACK — NOT FOR COMPLIANCE USE",
        "Rules below were assembled from secondary reporting and have not",
        "been read from primary sources.",
        f"Unverified: {joined}",
        "See docs/policy-sources.md. --strict refuses unverified verdicts.",
    ]
    out = ["╔" + "═" * _BANNER_W + "╗"]
    out += ["║  " + ln.ljust(_BANNER_W - 2) + "║" for ln in lines]
    out.append("╚" + "═" * _BANNER_W + "╝")
    return "\n".join(out)


def render(matrix: Matrix, conflicts: list[Conflict]) -> str:
    out: list[str] = []

    if matrix.has_unverified:
        out.append(_banner(matrix.unverified_packs))
        out.append("")

    if matrix.draft_rules:
        out.append("⚠ DRAFT SOURCE — these rules cite a document that is still a "
                   "draft; their dates are proposed and may move:")
        for rid in matrix.draft_rules:
            out.append(f"    {rid}")
        out.append("")

    name_w = max([len(r.display) for r in matrix.rows] + [len("ASSET")]) + 2
    purpose_w = max([len(r.purpose) for r in matrix.rows] + [len("PURPOSE")]) + 2
    col_w = max([len(j) for j in matrix.jurisdictions] + [6]) + 2

    header = f"{'ASSET':<{name_w}}{'PURPOSE':<{purpose_w}}" + "".join(
        f"{j:<{col_w}}" for j in matrix.jurisdictions)
    out.append(header)
    out.append("─" * len(header))

    for row in matrix.rows:
        line = f"{row.display:<{name_w}}{row.purpose:<{purpose_w}}" + "".join(
            f"{row.cells[j].verdict.value:<{col_w}}" for j in matrix.jurisdictions)
        if row.conflict_ids:
            line += "  ⚠ " + ",".join(row.conflict_ids)
        out.append(line)

        detail = []
        if row.risk and row.risk.band in ("critical", "high"):
            detail.append(f"{row.risk.band} · exposure {row.risk.exposure_years}y "
                          f"· {row.risk.rationale}")
        if row.unscored:
            span = row.unscored.range_if_guessed
            span_txt = (" · ".join(f"{k.replace('_',' ')} → {v}" for k, v in span.items())
                        if span else "")
            detail.append(f"unresolved: {row.unscored.reason}"
                          + (f" ({row.unscored.signal})" if row.unscored.signal else ""))
            if span_txt:
                detail.append(span_txt)
            detail.append(row.unscored.would_resolve)
        if row.locations:
            detail.append(row.locations[0])
        for d in detail:
            out.append(f"{'':<{name_w}}└ {d}")

    if conflicts:
        out.append("")
        out.append(f"CONFLICTS ({len(conflicts)})")
        for c in conflicts:
            out.append(f"  {c.id}  [{c.kind}]  {c.display}")
            out.append(f"      {c.summary}")
            if c.satisfies_all:
                out.append(f"      satisfies all: {c.satisfies_all}")
            if c.cost_note:
                out.append(f"      {c.cost_note}")
    else:
        out.append("")
        out.append("CONFLICTS (0) — the selected jurisdictions do not disagree "
                   "about any asset here.")

    a = matrix.assumptions
    out.append("")
    out.append(f"Assumptions: CRQC {a['crqc_year']} ({a['crqc_note']}) · "
               f"migration {a['migration_years']}y · "
               f"system_category {a['system_category'] or 'undeclared'}")

    counts: dict[str, int] = {}
    for row in matrix.rows:
        counts[row.worst.value] = counts.get(row.worst.value, 0) + 1
    out.append("Summary: " + " · ".join(f"{k} {v}" for k, v in sorted(counts.items())))
    if Verdict.INDETERMINATE.value in counts and not matrix.strict:
        out.append("         INDET findings do not fail the build. Use "
                   "--strict to make them exit 3.")
    return "\n".join(out)
