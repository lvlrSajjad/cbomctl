"""Markdown report, for PR comments and CI summaries."""

from __future__ import annotations

from cbomctl.models import Conflict
from cbomctl.verdict.matrix import Matrix


def render(matrix: Matrix, conflicts: list[Conflict]) -> str:
    out: list[str] = ["# cbomctl verdict", ""]

    if matrix.has_unverified:
        out += [
            "> [!WARNING]",
            "> **UNVERIFIED POLICY PACK — not for compliance use.**",
            f"> Rules from {', '.join(f'`{p}`' for p in matrix.unverified_packs)} were "
            "assembled from secondary reporting and have not been read from primary "
            "sources. See `docs/policy-sources.md`.",
            "",
        ]

    cols = " | ".join(f"`{j}`" for j in matrix.jurisdictions)
    out += [f"| Asset | Purpose | {cols} | |",
            "|---|---|" + "---|" * len(matrix.jurisdictions) + "---|"]
    for r in matrix.rows:
        cells = " | ".join(r.cells[j].verdict.value for j in matrix.jurisdictions)
        flag = ", ".join(r.conflict_ids)
        out.append(f"| `{r.display}` | {r.purpose} | {cells} | {flag} |")

    out += ["", f"## Conflicts ({len(conflicts)})", ""]
    if not conflicts:
        out.append("The selected jurisdictions do not disagree about any asset here.")
    for c in conflicts:
        out += [f"### `{c.id}` — {c.display} ({c.kind})", "", c.summary, ""]
        if c.satisfies_all:
            out.append(f"**Satisfies all:** {c.satisfies_all}")
        if c.cost_note:
            out += ["", c.cost_note]
        out.append("")

    unresolved = [r for r in matrix.rows if r.unscored]
    if unresolved:
        out += [f"## Unresolved ({len(unresolved)})", "",
                "The CBOM does not say what these are for, so they are not scored.", ""]
        for r in unresolved:
            span = " · ".join(f"{k.replace('_', ' ')} → **{v}**"
                              for k, v in r.unscored.range_if_guessed.items())
            out.append(f"- `{r.display}` — {r.unscored.reason}"
                       + (f" ({span})" if span else "")
                       + f" {r.unscored.would_resolve}")
        out.append("")

    a = matrix.assumptions
    out += ["## Assumptions", "",
            f"- CRQC year **{a['crqc_year']}** — {a['crqc_note']}",
            f"- Migration time **{a['migration_years']} years**",
            f"- System category **{a['system_category'] or 'undeclared'}**", ""]
    return "\n".join(out)
