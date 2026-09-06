"""Terminal matrix. The default output."""

from __future__ import annotations

import shutil
import textwrap

from cbomctl.models import Conflict, Verdict
from cbomctl.verdict.matrix import Matrix

_BANNER_W = 74

#: Prose in the conflicts section is wrapped. Without this a conflict note is
#: emitted as a single line -- the four-jurisdiction case reaches 439
#: characters -- which a terminal soft-wraps into an unreadable block and a
#: <pre> in a browser does not wrap at all.
_MIN_W, _MAX_W = 60, 100


def _wrap(text: str, indent: str) -> list[str]:
    """Wrap prose to the terminal width, clamped to something readable."""
    width = shutil.get_terminal_size(fallback=(100, 24)).columns
    width = max(_MIN_W, min(_MAX_W, width)) - len(indent) - 4
    return [indent + line for line in textwrap.wrap(text, width=width)] or [indent.rstrip()]


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
        # Two assets can share a verdict for different reasons and on different
        # dates -- RSA-2048 and RSA-3072 both WARN under IR 8547, one
        # deprecated in 2030 and one only disallowed in 2035. The matrix cell
        # cannot show that; this line can.
        for jid in matrix.jurisdictions:
            cell = row.cells[jid]
            dated = [(r.deadline_state.value if r.deadline_state else "due",
                      r.deadline) for r in cell.rules if r.deadline]
            if not dated:
                continue
            seen: dict[str, str] = {}
            for state, when in sorted(dated, key=lambda d: d[1]):
                seen.setdefault(state, when.isoformat())
            detail.append(f"{jid} · " + " · ".join(
                f"{k} {v}" for k, v in seen.items()))

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
            wrapped = _wrap(d, "")
            out.append(f"{'':<{name_w}}└ {wrapped[0]}")
            for cont in wrapped[1:]:
                out.append(f"{'':<{name_w}}  {cont}")

    if conflicts:
        out.append("")
        out.append(f"CONFLICTS ({len(conflicts)})")
        for c in conflicts:
            out.append(f"  {c.id}  [{c.kind}]  {c.display}")
            out += _wrap(c.summary, "      ")
            if c.satisfies_all:
                out += _wrap(f"satisfies all: {c.satisfies_all}", "      ")
            if c.cost_note:
                out += _wrap(c.cost_note, "      ")
            if c.alternative_reading:
                out += _wrap(f"⚖ {c.alternative_reading}", "      ")
    else:
        out.append("")
        out.append("CONFLICTS (0) — the selected jurisdictions do not disagree "
                   "about any asset here.")

    a = matrix.assumptions
    out.append("")
    out += _wrap(
        f"Assumptions: CRQC {a['crqc_year']} ({a['crqc_note']}) · "
        f"migration {a['migration_years']}y · "
        f"system_category {a['system_category'] or 'undeclared'}", "")

    counts: dict[str, int] = {}
    for row in matrix.rows:
        counts[row.worst.value] = counts.get(row.worst.value, 0) + 1
    out.append("Summary: " + " · ".join(f"{k} {v}" for k, v in sorted(counts.items())))
    if Verdict.INDETERMINATE.value in counts and not matrix.strict:
        out.append("         INDET findings do not fail the build. Use "
                   "--strict to make them exit 3.")
    return "\n".join(out)
